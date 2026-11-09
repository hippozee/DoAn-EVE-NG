# Danh mục minh chứng và nguồn

Mốc repo trước bổ sung docs: c04f55196230c5aff2c9e0d1dcb5845d40b3ef2f. Đã đọc các tệp text/topology dưới đây. Chưa đọc ba Word và chưa phân tích hai ảnh PNG trong lần bổ sung này.

## Nguồn trong repo

| Nguồn | Nội dung đã đọc / mức sử dụng |
|---|---|
| [Topology](../DoAn_HQ_BR1_BR2.unl) | Node, image, interface và network_id; không chứa đầy đủ cấu hình Linux của từng VM |
| [HQ FRR](../HQ_FRR.txt) | FRR 8.4.4, Router-ID 10.255.0.1, LAN passive, WAN cost 10 |
| [BR2 FRR](../BR2_FRR.txt) | Router-ID 10.255.0.3, wg0 NBMA cost 5, hello/dead 2/8, neighbor |
| [BR1 terminal](../BR1.txt) | Đầu tệp có FRR BR1; phần còn lại có NUL, escape terminal và lệnh lỗi. Chỉ trích phần hợp lệ; không thực thi nguyên tệp |
| [HQ snapshot](../HQ_CHECK.txt) | Interface, Linux route, OSPF Full, FRR route |
| [BR1 snapshot](../BR1_check.txt) | LAN/WAN/underlay/wg0; route tới LAN BR2 qua wg0 |
| [BR2 snapshot](../BR2_CHECK.txt) | LAN/WAN/underlay/wg0; route tới LAN BR1 qua wg0 |
| [Thư mục Word](../DoAn_EVE) | Ba tài liệu cũ: Cam_nang_trien_khai_do_an_Network_AI.docx, Mau_1_Hoan_thien_Network_AI.docx, Mau_2_Hoan_thien_Network_AI.docx; cần đọc trước khi dùng |
| [Ảnh 05/11](../Screenshot%202026-11-05%20153058.png) | Có tệp; chưa phân tích, chưa dùng làm bằng chứng nội dung |
| [Ảnh tên QoS](../screenshotsqos_test.png.png) | Có tệp; tên không đủ chứng minh QoS đạt |

Tệp chỉ có FRR/routing không đủ chứng minh nftables/iptables, NAT, QoS hoặc WireGuard private/peer configuration.

## Bằng chứng quan sát trong chat ngày 09/11

Các ảnh dưới đây chưa được sao chép vào repo. Mã E là mã chỉ mục tài liệu, không phải tên tệp hay ID ảnh. Muốn đưa vào báo cáo/slide cần lấy đúng ảnh người dùng cung cấp và kiểm tra nội dung.

| Mã | Quan sát trong ảnh/trao đổi | Kết luận được phép |
|---|---|---|
| E01 | systemctl thấy Zabbix Server/Agent running; /opt/network-ai có venv | Dịch vụ Zabbix và môi trường Python tồn tại |
| E02 | pip show NumPy/scikit-learn; chương trình import requests chạy | Có thư viện cho bước thử nghiệm |
| E03 | apiinfo.version trả 7.0.31 | API local hoạt động và phiên bản trả về |
| E04 | user.login và host/item listing thành công | Tài khoản dùng trong phiên có quyền đọc dữ liệu tương ứng |
| E05 | Templates có ICMP Ping ở cả ba router | Template đã liên kết |
| E06 | Ba router có ping=1, loss=0, RTT và lastclock mới | Có mẫu ICMP thực tại thời điểm ảnh |
| E07 | ai_check.py chạy không hỏi mật khẩu, in số mẫu dưới 30 | Đọc dữ liệu tự động được; chưa chứng minh mô hình đã học |
| E08 | Journal có nhiều lần Starting/Finished, đầu ra từng host | Có chạy định kỳ thành công ở mức tiến trình |
| E09 | Latest data có Network AI report; người dùng nói Last value trống | Item tồn tại; chưa nghiệm thu ingest dữ liệu |
| E10 | Journal lỗi Allowed hosts của history.push | Đã xác định nhóm lỗi; chưa xác định chính xác IP nguồn frontend |
| E11 | Sender thử và publisher thật đều processed: 1; failed: 0 | Đường gửi mới buộc nguồn/đích 127.0.0.1 hoạt động |
| E12 | Dashboard AI Network Analysis có report 17:22:44 với HQ 64, BR1 67, BR2 66 mẫu và score | Đã đủ mẫu, suy luận và hiển thị báo cáo thật; chưa chứng minh độ chính xác |
| E13 | Global view hiển thị server 7.0.31, frontend 7.0.32 sau cài sender | Phải phân biệt phiên bản thành phần; không mặc định server đã chạy 7.0.32 |

Không biến các dòng log Finished thành bằng chứng độ chính xác AI; chương trình có nhánh bắt lỗi vẫn có thể thoát mã 0.

## Gói minh chứng cần bổ sung trước bản nộp

- Ảnh topology hiện tại đủ nhãn và kết nối; cấu hình mới nếu khác snapshot.
- Cấu hình Linux networking, FRR, WireGuard đã che khóa; handshake/counters.
- Firewall/QoS đã che thông tin nhạy cảm, kèm test từ đúng LAN.
- Mã AI thật từ VM, requirements và units thực tế, không kèm credentials/venv.
- Export cấu hình Zabbix đã loại bí mật; bảng item và lịch sử có timestamp.
- Thu lại đúng ảnh báo cáo ai.report/widget/nhật ký gửi thành công đã có trong chat để lưu vào hồ sơ minh chứng; hiện chỉ mô tả và số đọc từ ảnh được lưu trong tài liệu.
- Bộ CSV và ảnh cho từng Test ID, gồm baseline/sự cố/phục hồi.
- Word bản thảo được người dùng chọn và hướng dẫn định dạng của trường.
- Thông tin bìa và tên đề tài chính thức do người dùng xác nhận.

## Cách đặt tên và chú thích

Ví dụ đường dẫn dự kiến: evidence/YYYYMMDD/T10/run01_rtt_before.png, run01_rtt_during.png, run01_ai.log, run01_metrics.csv. Đây là đề xuất đặt tên, chưa phải tệp đã tồn tại.

Mỗi ảnh cần caption: test/node/lệnh hoặc màn hình, thời điểm có múi giờ, điều ảnh chứng minh và nguồn gốc. Không đưa password/token/private key vào ảnh, code, Git hay slide. Nếu ảnh cắt mất Last value hoặc timestamp thì không dùng để khẳng định đã cập nhật.
