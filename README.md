# Đồ án mạng HQ – BR1 – BR2 với Zabbix và AI

Mô phỏng mạng nhiều cơ sở trên EVE-NG, dùng Debian 12 + FRRouting để định tuyến OSPF, kết nối BR1–BR2 qua giao diện WireGuard và giám sát bằng Zabbix. Phần AI thử nghiệm dùng Isolation Forest để phát hiện độ trễ khác thường.

**Mốc kiểm thử mới nhất: 13/11/2026, giờ Việt Nam.** Xem [biên bản kiểm thử](Bien_ban_kiem_thu_EVE_NG.md) để đối chiếu kết quả trên lab.

**Đọc tiến độ ngày 10/11:** [Tiến độ 10/11 — thẻ AI, graph RTT và đồng bộ giờ](docs/PROGRESS_2026-11-10.md). Mốc này bổ sung và thay thế các trạng thái cũ tương ứng trong hồ sơ 09/11.

## Đọc trước khi tiếp tục bằng Codex

1. [Ngữ cảnh dự án và bản đồ cấu hình](docs/CODEX_CONTEXT.md).
2. [Tiến độ và bằng chứng ngày 09/11](docs/PROGRESS_2026-11-09.md).
3. [Vận hành và giới hạn phần AI](docs/AI_RUNBOOK.md).
4. [Kế hoạch kiểm thử](docs/TEST_PLAN.md).
5. [Dàn ý báo cáo](docs/REPORT_OUTLINE.md).
6. [Dàn ý 12 slide](docs/SLIDES_OUTLINE.md).
7. [Danh mục minh chứng](docs/EVIDENCE_INDEX.md).

## Đã xác nhận đến mốc cập nhật

- Các bản xuất cấu hình trong repo ghi nhận OSPF neighbor Full và tuyến BR1–BR2 qua wg0.
- Ảnh thao tác ngày 09/11 xác nhận Zabbix API 7.0.31, đăng nhập API thành công, cả ba router có dữ liệu ICMP.
- Chương trình AI trên máy Zabbix đọc được dữ liệu thực, tự đăng nhập và được dịch vụ systemd chạy nhiều lần thành công.
- Cả ba router đã đủ mẫu và có nhãn/decision score: ảnh dashboard 17:22:44 ngày 09/11 ghi HQ 64, BR1 67, BR2 66 mẫu; cả ba được mô hình gắn nhãn RTT bình thường tại thời điểm đó.
- Đã chuyển publisher sang zabbix_sender, chỉ định nguồn/đích 127.0.0.1. Nhật ký xác nhận processed: 1; failed: 0 và báo cáo thật đã hiển thị trên dashboard riêng **AI Network Analysis**.
- Ngày 10/11 đã tạo 9 item số, chuyển sang publish_ai_cards.py và quan sát sender nhận đủ 10 giá trị. Dashboard có ba thẻ trạng thái và Graph RTT ba đường với timestamp ngày 10/11.
- Đồng hồ SERVER-ZABBIX đã được chrony đồng bộ lại; còn cần kiểm tra các router và khả năng giữ giờ sau suspend/reboot.
- Đã xác nhận luồng đọc → phân tích → gửi → hiển thị và [một lần thử T10 tăng RTT BR1, phát hiện và phục hồi](docs/tests/T10_RTT_BR1_2026-11-10.md). Chưa đánh giá độ chính xác, tỷ lệ cảnh báo nhầm hoặc thời gian phát hiện định lượng.

Đã nhận [mã AI thực tế, units và requirements từ VM](ai/README.md), kèm [log T10 gốc và CSV trích xuất](evidence/ai/2026-11-10). Gói qua kiểm tra toàn vẹn; không chứa credentials.json. Đây là bản sao nguồn đã xuất, không phải kiểm tra trực tiếp trạng thái VM hiện tại.

- Bổ sung kiểm tra cuối buổi: [T12 mất phản hồi ICMP BR1 và phục hồi](docs/tests/T12_ICMP_BR1_2026-11-10.md), [T15 AI tự chạy sau reboot SERVER-ZABBIX](docs/tests/T15_REBOOT_2026-11-10.md). Đã có kết quả chức năng theo ảnh; chưa đánh giá độ chính xác ML hoặc độ trễ phát hiện.

## Tệp hiện có

| Nhóm | Nguồn |
|---|---|
| Topology EVE-NG | [DoAn_HQ_BR1_BR2.unl](DoAn_HQ_BR1_BR2.unl) |
| FRR HQ / BR2 | [HQ_FRR.txt](HQ_FRR.txt), [BR2_FRR.txt](BR2_FRR.txt) |
| FRR BR1 và bản ghi terminal | [BR1.txt](BR1.txt), cần tách phần cấu hình khỏi log và ký tự điều khiển trước khi dùng |
| Snapshot interface, route, OSPF | [HQ_CHECK.txt](HQ_CHECK.txt), [BR1_check.txt](BR1_check.txt), [BR2_CHECK.txt](BR2_CHECK.txt) |
| AI từ VM | [Mã, cấu hình và hướng dẫn](ai/README.md); [manifest SHA-256](ai/backup_manifest.json) |
| Nhật ký/CSV T10 | [Minh chứng AI 10/11](evidence/ai/2026-11-10) |
| Tài liệu Word cũ | [DoAn_EVE](DoAn_EVE), cần đọc nội dung trước khi tái sử dụng |
| Ảnh cũ | Hai tệp PNG ở thư mục gốc; chưa được phân tích trong lần bổ sung hồ sơ này |

Các snapshot không phải cấu hình lấy trực tiếp từ lab ngày 09/11. Không chạy nguyên tệp log BR1 vào shell. Không đưa credentials.json, mật khẩu, API token hoặc khóa riêng WireGuard vào repo.

## Việc ưu tiên

Đã sao lưu mã AI/units/requirements và log T10. Phần bàn giao còn cần bản export của topology mở rộng, cấu hình khởi động tương ứng và minh chứng cho báo cáo, slide. Bản `.unl` liệt kê ở trên là bản đã lưu trong kho. Cần đối chiếu với topology đang chạy trước khi dùng để tái tạo lab.

Biên bản ngày 13/11 đã ghi nhận kết quả đo QoS theo chiều chi nhánh về HQ, kiểm tra chuyển tuyến khi ngắt riêng từng WAN chính và demo AI khi tăng RTT hoặc mất phản hồi ICMP. Thời gian hội tụ và độ chính xác của mô hình AI vẫn cần phép đo riêng.
