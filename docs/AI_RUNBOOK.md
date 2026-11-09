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
8. Bản hoạt động hiện tại là publish_ai_sender.py: chạy ai_check.py như subprocess, thêm timestamp, rồi gửi stdout vào ai.report bằng zabbix_sender, nguồn/đích 127.0.0.1, host kỹ thuật Zabbix server, key ai.report. Kiểm tra returncode và processed: 1; failed: 0 trước in thông báo thành công.
9. Bản cũ publish_ai.py dùng history.push và gặp lỗi địa chỉ nguồn; không dùng lẫn với bản sender đã hoạt động.

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

ExecStart hiệu lực hiện tại phải là /opt/network-ai/venv/bin/python -u /opt/network-ai/publish_ai_sender.py, không chỉ ai_check.py hoặc bản publish_ai.py cũ. Có override publish.conf trong thư mục network-ai-check.service.d; dùng systemctl cat để kiểm tra cấu hình hợp nhất.

## Sự cố đã gặp: item có nhưng Last value trống

history.push đã trả error ở phần tử itemid 51184: Connection source address is not in item's allowed hosts list. Zabbix 7.0 kiểm tra cả IP client và nguồn kết nối từ frontend. Chưa xác định chính xác nguồn frontend trong lab; không kết luận chắc do IPv6.

Đường gửi hiện tại dùng zabbix_sender với -z 127.0.0.1 -I 127.0.0.1 -s "Zabbix server" -k ai.report. Dữ liệu thử được nhận, rồi publisher gửi báo cáo thật thành công; widget đã hiển thị nội dung.

Nếu tái diễn:
1. Xác nhận ExecStart đang dùng publish_ai_sender.py, xem log mới thay vì lỗi cũ.
2. Kiểm tra item ai.report đúng hostid 10084, type 2, value_type 4, status 0; giữ 127.0.0.1 trong Allowed hosts.
3. Xem stderr, returncode và processed/failed của sender; kiểm tra cổng 10051, host kỹ thuật, key, TLS policy và cấu hình item khi có lỗi tương ứng.
4. Item mới có thể cần chờ cache; không tạo bản trùng.
5. Nếu sender nhận mà widget chưa hiện: kiểm tra Latest data/History, filter, timestamp và preprocessing.

Không đưa nội dung credentials.json vào ảnh hoặc log. Không xóa Allowed hosts hoặc mở toàn mạng để né lỗi.

## Hiển thị trên dashboard sau khi có giá trị

Dashboard riêng **AI Network Analysis** → Edit dashboard → Add widget:
- Type: Item history.
- Name: Bao cao Network AI.
- Columns → Add → chọn Network AI report thuộc Zabbix server.
- Display: As is, để giữ xuống dòng; dùng monospace nếu cần.
- Show lines: 1 (một bản ghi báo cáo mới nhất).
- Bật timestamp trong Advanced configuration, refresh phù hợp rồi Save dashboard.

Ảnh thực tế đã xác nhận Item history hiển thị đủ nội dung báo cáo. Giữ dashboard WAN hiện tại riêng cho biểu đồ mạng; AI Network Analysis dành cho kết quả phân tích. Mỗi báo cáo nhiều dòng là một bản ghi; Show lines=1 chỉ giữ bản ghi mới nhất, không cắt báo cáo thành một dòng.

Timestamp trong report có +00:00 còn UI hiển thị giờ Việt Nam là cùng thời điểm khi chênh 7 giờ; không đổi giờ hệ thống chỉ vì khác cách hiển thị.

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

1. Đã có gửi/hiển thị báo cáo; còn cần cảnh báo nodata và xác nhận sau reboot.
2. Đồng bộ, gắn nhãn và xuất dữ liệu thí nghiệm; tạo baseline khỏe cố định.
3. Lưu mô hình và metadata (thời gian học, số mẫu, ID item, phiên bản).
4. Thêm jitter/loss/lưu lượng khi có dữ liệu phù hợp; đánh giá riêng từng đặc trưng.
5. Đổi tài khoản Admin sang tài khoản dịch vụ chỉ đủ quyền cần thiết sau khi thử nghiệm hoạt động.
6. Đưa bản mã thật từ VM lên repo sau khi bỏ thông tin đăng nhập. Không đưa venv, database hay khóa riêng vào Git.

## Tài liệu kỹ thuật

- [API Zabbix 7.0](https://www.zabbix.com/documentation/7.0/en/manual/api)
- [history.get](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/history/get)
- [history.push — bản publisher trước](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/history/push)
- [zabbix_sender — đường gửi hiện tại](https://www.zabbix.com/documentation/7.0/en/manpages/zabbix_sender)
- [item.create](https://www.zabbix.com/documentation/7.0/en/manual/api/reference/item/create)
- [Item history widget](https://www.zabbix.com/documentation/7.0/en/manual/web_interface/frontend_sections/dashboards/widgets/item_history)
- [IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
