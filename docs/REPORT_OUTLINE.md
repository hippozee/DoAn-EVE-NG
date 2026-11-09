# Khung báo cáo đồ án

Đây là dàn ý có đoạn dẫn để Codex phát triển thành báo cáo, chưa phải bản Word cuối. Chỉ dùng các kết quả đã được PROGRESS và EVIDENCE_INDEX xác nhận. Trước khi định dạng phải đọc bản hướng dẫn trình bày của trường, tài liệu Word cũ và bản thảo người dùng chọn.

## Thông tin cần chốt

Tên đề tài chính thức; tên sinh viên, mã sinh viên, lớp; giảng viên; tên bộ môn/khoa; hạn nộp; mẫu bìa; quy định font, lề, trích dẫn và độ dài. Không lấy tên chủ tài khoản làm tên sinh viên.

## Tóm tắt dự kiến

Đồ án xây dựng mô hình mạng gồm một trụ sở chính và hai chi nhánh trong môi trường EVE-NG. Các router Linux sử dụng FRRouting để trao đổi tuyến OSPF; kết nối logic giữa hai chi nhánh được triển khai qua giao diện WireGuard. Zabbix thu thập khả năng kết nối, mất gói và độ trễ ICMP. Thành phần Python khai thác lịch sử độ trễ để thử nghiệm phát hiện mẫu khác thường bằng Isolation Forest, kết hợp quy tắc riêng cho mất kết nối và mất gói. Phần đánh giá cuối phải bổ sung kết quả kiểm thử thực tế, giới hạn của dữ liệu và kết quả tích hợp dashboard.

Đoạn trên mô tả phạm vi. Không bổ sung câu đã đạt độ chính xác hay hội tụ nhanh khi chưa đo.

## Chương 1 — Bài toán và yêu cầu

- Bối cảnh: nhiều cơ sở cần kết nối và giám sát tập trung, đồng thời hỗ trợ luồng trao đổi giữa chi nhánh.
- Yêu cầu chức năng: liên thông LAN; chọn tuyến; kênh BR1–BR2; theo dõi trạng thái; cảnh báo và hiển thị kết quả phân tích.
- Yêu cầu phi chức năng: phục hồi khi có lỗi, chính sách truy cập, chi phí triển khai mô phỏng, khả năng tái lập.
- Phạm vi: lab EVE-NG; chưa khẳng định đáp ứng SLA hay tải doanh nghiệp.
- Bảng yêu cầu → cách triển khai → test ID trong TEST_PLAN.
- Vai trò HQ về nghiệp vụ/quản trị phải được chuyển thành policy kiểm thử được; không suy ra đặc quyền từ OSPF.

## Chương 2 — Cơ sở kỹ thuật

| Nội dung | Cần giải thích gắn với đồ án |
|---|---|
| EVE-NG, Debian, FRR | Vai trò hypervisor/lab và router phần mềm |
| OSPF | Area, Router-ID, neighbor, cost, passive interface, hội tụ |
| WireGuard | Tunnel/underlay, peer, khóa, handshake; không đưa khóa thật vào báo cáo |
| Phân quyền và QoS | Firewall cho phép/chặn khác với ưu tiên khi có tắc nghẽn |
| Zabbix | Host, interface, template, item, trigger, history, API, dashboard |
| Isolation Forest | Học không giám sát, bất thường, decision score và giới hạn |
| Đánh giá | Baseline, tập kiểm thử độc lập, false positives và độ trễ phát hiện |

Dùng nguồn chính thức cho mô tả API/thuật toán; trích dẫn theo quy định của trường. Không sao chép nguyên văn dài từ tài liệu.

## Chương 3 — Thiết kế hệ thống

- Topology vật lý/ảo từ .unl và sơ đồ logic OSPF/WireGuard tách biệt.
- Bảng địa chỉ, interface và node lấy từ CODEX_CONTEXT; đối chiếu lab hiện tại trước khi chốt.
- Kịch bản chọn đường: BR1–BR2 qua wg0 cost 5, các WAN HQ cost 10 trong snapshot.
- Chính sách kết nối giữa các LAN; cần ma trận source/destination/service/action thực tế.
- Vị trí Zabbix và đường truy cập tới router. Xác định đường đo để giải thích RTT và test lỗi.
- Thiết kế AI: input, kiểm tra chất lượng dữ liệu, nhánh quy tắc, nhánh RTT ML, output báo cáo.
- Phân biệt phát hiện bất thường, chẩn đoán nguyên nhân và tự phục hồi: bản hiện tại chỉ thực hiện phần phát hiện/hiển thị.

Hình cần có: topology thật, sơ đồ logic, sơ đồ luồng dữ liệu Zabbix → Python → báo cáo → dashboard. Gắn nhãn phần chưa nghiệm thu.

## Chương 4 — Triển khai

1. Môi trường: cấu hình máy chạy lab chỉ điền từ thông tin đã xác nhận; phiên bản theo bằng chứng.
2. Node Debian/FRR, network và mapping interface; lưu cấu hình.
3. OSPF và kiểm tra neighbor/route bằng lệnh trong TEST_PLAN.
4. WireGuard và kiểm tra handshake/counters đã che thông tin khóa.
5. Firewall/QoS: chỉ trình bày rule/class đã có bản xuất và kiểm thử.
6. Zabbix API/server ban đầu 7.0.31, frontend sau cài sender hiển thị 7.0.32; ghi phiên bản từng thành phần theo ảnh. ICMP Ping template cho ba router, ánh xạ item ID.
7. Python venv, requests/NumPy/scikit-learn, ai_check.py và credentials cục bộ không nhúng vào tài liệu.
8. systemd oneshot/timer và nhật ký tự chạy.
9. Publisher ai.report dùng zabbix_sender nguồn/đích 127.0.0.1 và widget Item history trên dashboard riêng AI Network Analysis đã hiển thị báo cáo thật. Ghi lỗi Allowed hosts của bản history.push là vấn đề triển khai đã chuyển đường gửi, không suy ra đã sửa nguyên nhân gốc.

Ảnh terminal cần cắt gọn phần có ý nghĩa, chú thích node/lệnh/thời gian. Không dùng ảnh chỉ có lệnh đã gõ để chứng minh kết quả.

## Chương 5 — Kiểm thử, đánh giá và kết luận

- Phương pháp: baseline, các test T01–T15, cách đo, điều kiện và phục hồi.
- Kết quả mạng: đường đi và failover, firewall, QoS khi có số đo.
- Kết quả giám sát: dữ liệu mới, cảnh báo, báo cáo và dashboard.
- Kết quả AI: đủ mẫu, phân bố score, mẫu khỏe/bất thường có nhãn, lỗi và cảnh báo nhầm.
- So sánh mục tiêu với kết quả thực tế; ghi rõ chưa hoàn thành hoặc không đạt.
- Giới hạn: RTT một chiều đặc trưng, dữ liệu ít, refit liên tục, chưa baseline cố định, chưa chứng minh độ chính xác.
- Hướng phát triển: baseline cố định, đa đặc trưng, cảnh báo nodata, tài khoản dịch vụ tối thiểu, mô hình lưu phiên bản.

Không điền trước thời gian hội tụ, throughput, phần trăm giảm chi phí/băng thông hoặc độ chính xác. Nếu chưa có phép đo thì ghi chưa đánh giá.

## Phụ lục

- Bảng IP và item ID (ghi phạm vi database).
- Cấu hình đã loại bỏ bí mật, kèm commit/thời điểm.
- Danh sách lệnh kiểm tra; mẫu nhật ký, bảng kết quả, CSV.
- Hướng dẫn khởi động/tắt lab và phục hồi.
- Danh mục ảnh với liên kết nguồn.

## Nguồn để viết

Đọc CODEX_CONTEXT → PROGRESS → AI_RUNBOOK → TEST_PLAN → EVIDENCE_INDEX, rồi kiểm tra tệp cấu hình gốc. Tài liệu Word trong DoAn_EVE là nguồn cũ chưa đọc trong lần bổ sung này; không mặc định nội dung trong đó là hệ thống hiện tại.
