# Vận hành phần AI và Zabbix

Mốc 09/11/2026. Mã chương trình trên VM được người dùng dán từ hướng dẫn trong chat; chưa được tải từ VM và đối chiếu byte với repo. Tài liệu này mô tả hành vi của bản đã hướng dẫn và các kết quả đã thấy, không phải bản sao lưu mã nguồn.

## Luồng xử lý

1. ai_check.py đăng nhập API local bằng credentials.json.
2. Đọc 9 item ICMP đã ánh xạ trong PROGRESS_2026-11-09.md.
3. Kiểm tra thiếu item, status/state và độ mới lastclock. Dữ liệu chưa từng có hoặc lệch thời gian quá 180 giây được coi là cũ/lỗi, không kết luận mạng.
4. icmpping=0 → quy tắc mất kết nối. Loss>0 → quy tắc mất gói.
5. Với kết nối tốt, lấy lịch sử RTT 24 giờ, tối đa 500 mẫu, trước lastclock của mẫu hiện tại; chỉ giữ giá trị >0 và đổi giây sang ms.
6. Chưa đủ 30 mẫu → CHO DU LIEU. Ít hơn 5 giá trị RTT phân biệt → chưa đánh giá.
7. Fit IsolationForest một chiều RTT: n_estimators=100, contamination=auto, random_state=42, n_jobs=1; đánh giá mẫu hiện tại bằng predict và decision_function.
8. Bản publisher đã hướng dẫn chạy ai_check.py như subprocess, thêm timestamp có timezone, rồi gửi toàn bộ stdout vào ai.report qua history.push.

## Ý nghĩa đầu ra

| Đầu ra | Diễn giải |
|---|---|
| CHO DU LIEU | Chưa huấn luyện; không đồng nghĩa bình thường |
| DU LIEU CU/LOI | Không đủ căn cứ đánh giá trạng thái mạng hiện tại |
| QUY TAC: MAT KET NOI | Ping ICMP mới nhất bằng 0 |
| QUY TAC: CO MAT GOI | Mất gói mới nhất lớn hơn 0 |
| AI: RTT BINH THUONG | Mẫu nằm phía bình thường theo mô hình hiện tại |
| AI: NGHI NGO BAT THUONG RTT | Mẫu bị mô hình gắn nhãn -1; cần kiểm chứng |
| decision_score | Điểm quyết định mô hình, không phải xác suất hoặc phần trăm chính xác |

Bản hiện tại không dùng LLM, không tự sửa route, không cấu hình firewall và không tự khôi phục mạng. Thuật toán ML chỉ phân tích RTT; ping/loss là quy tắc. Không gọi cả ba phép kiểm tra là dự đoán bằng AI.

## Chạy và xem log

```bash
/opt/network-ai/venv/bin/python /opt/network-ai/ai_check.py
systemctl list-timers network-ai-check.timer --no-pager
systemctl status network-ai-check.timer --no-pager
systemctl cat network-ai-check.service
journalctl -u network-ai-check.service -n 50 --no-pager
```

Service là Type=oneshot: inactive sau khi hoàn thành không tự nó là lỗi. Timer cấu hình OnUnitInactiveSec=60s: khoảng 60 giây sau khi lần chạy trước kết thúc, không phải chính xác mỗi mốc phút. Thời gian phân tích/API cộng vào chu kỳ.

Sau khi publisher được xác nhận, ExecStart hiệu lực phải là publish_ai.py, không chỉ ai_check.py. Có override publish.conf trong thư mục network-ai-check.service.d; dùng systemctl cat để kiểm tra cấu hình hợp nhất.

## Sự cố hiện tại: item có nhưng Last value trống

Kiểm tra theo thứ tự:

1. Xem nhật ký vừa chạy: có DA TAO ITEM, DA GUI BAO CAO LEN ZABBIX hay LOI PUBLISH?
2. Nếu mới tạo: cache cấu hình có thể chưa cập nhật; lần chạy sau mới gửi. Kiểm tra lại sau 1–2 phút, không tạo bản trùng.
3. Kiểm tra timer enabled/active, ExecStart hiệu lực và đường dẫn publisher.
4. Kiểm tra item ai.report thuộc đúng hostid 10084; type 2 (trapper), value_type 4 (Text), status 0 (enabled).
5. Đối chiếu lỗi từng phần tử history.push. Kết quả API tổng thể success chưa đủ nếu phần tử có error.
6. Kiểm tra quyền API history.push, trạng thái host, maintenance, Allowed hosts và địa chỉ nguồn được Zabbix nhìn thấy. Hướng dẫn đặt Allowed hosts 127.0.0.1 vì gọi API local; xác nhận log trước khi đổi.
7. Nếu API báo nhận mà UI chưa hiện: xem History, lastclock, bộ lọc thời gian, múi giờ và preprocessing. Không đổi thông tin đăng nhập khi chưa có lỗi xác thực.

Lệnh thu thập cấu hình đọc:

```bash
systemctl cat network-ai-check.service
systemctl list-timers network-ai-check.timer --no-pager
journalctl -u network-ai-check.service -n 50 --no-pager
```

Không đưa nội dung credentials.json vào ảnh hoặc log hỗ trợ.

## Hiển thị trên dashboard sau khi có giá trị

Dashboard Network AI Monitoring → Edit dashboard → Add widget:
- Type: Item history.
- Name: Bao cao Network AI.
- Columns → Add → chọn Network AI report thuộc Zabbix server.
- Display: As is, để giữ xuống dòng; dùng monospace nếu cần.
- Show lines: 1 (một bản ghi báo cáo mới nhất).
- Bật timestamp trong Advanced configuration, refresh phù hợp rồi Save dashboard.

Trên Zabbix 7.0.31, dùng Item history cho báo cáo text. Nếu giao diện khác, đối chiếu ảnh trước khi hướng dẫn thêm.

## Giới hạn cần ghi trong báo cáo

- 30 mẫu là điều kiện khởi động demo do chương trình chọn, không phải kích thước chuẩn chứng minh chất lượng.
- Mô hình fit lại từ tối đa 500 mẫu RTT gần đây mỗi lần chạy; chưa lưu baseline/mô hình ổn định.
- Mẫu hiện tại bị loại theo timestamp để tránh tự huấn luyện trên chính mẫu đó. Tuy nhiên lịch sử chưa lọc đồng bộ theo ping/loss; các RTT từng ở trạng thái mạng suy giảm vẫn có thể vào tập học.
- Bất thường kéo dài có thể dần bị học như bình thường. Cần baseline khỏe đã kiểm tra và tập đánh giá riêng.
- Một chiều RTT không giải thích được nguyên nhân; chưa dùng jitter, lưu lượng, CPU, log hoặc trạng thái tunnel làm đặc trưng.
- Chưa đo precision, recall, F1, false positives hoặc độ trễ phát hiện. Không điền số giả.
- Chu kỳ ICMP khoảng một phút và timer phân tích khoảng một phút có thể bỏ lỡ sự cố ngắn. Đồng bộ thời gian và ghi lúc gây lỗi, lúc Zabbix có mẫu, lúc AI báo.
- Bản ai_check.py đã hướng dẫn bắt ngoại lệ rồi in LOI nhưng có thể vẫn exit 0. Vì vậy service Finished hoặc subprocess returncode=0 chưa đủ chứng minh phân tích thành công; kiểm tra nội dung từng host.
- Bản publisher gửi stdout dạng text; báo cáo chứa lỗi vẫn cần phân biệt với báo cáo bình thường. Nên bổ sung trạng thái lỗi có cấu trúc và cảnh báo dữ liệu không cập nhật.
- Chưa xác nhận phần trigger/cảnh báo chủ động; widget chỉ hiển thị thông tin.

## Mở rộng theo thứ tự ưu tiên

1. Chốt gửi báo cáo và cảnh báo nodata; xác nhận sau reboot.
2. Đồng bộ, gắn nhãn và xuất dữ liệu thí nghiệm; tạo baseline khỏe cố định.
3. Lưu mô hình và metadata (thời gian học, số mẫu, ID item, phiên bản).
4. Thêm jitter/loss/lưu lượng khi có dữ liệu phù hợp; đánh giá riêng từng đặc trưng.
5. Đổi tài khoản Admin sang tài khoản dịch vụ chỉ đủ quyền cần thiết sau khi thử nghiệm hoạt động.
6. Đưa bản mã thật từ VM lên repo sau khi bỏ thông tin đăng nhập. Không đưa venv, database hay khóa riêng vào Git.

## Tài liệu kỹ thuật

- [API Zabbix 7.0](https://www.zabbix.com/documentation/7.0/en/manual/api)
- [history.get](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/history/get)
- [history.push](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/history/push)
- [item.create](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/item/create)
- [Item history widget](https://www.zabbix.com/documentation/7.0/en/manual/web_interface/frontend_sections/dashboards/widgets/item_history)
- [IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
