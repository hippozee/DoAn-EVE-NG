# Đồ án mạng HQ – BR1 – BR2 với Zabbix và AI

Mô phỏng mạng nhiều cơ sở trên EVE-NG, dùng Debian 12 + FRRouting để định tuyến OSPF, kết nối BR1–BR2 qua giao diện WireGuard và giám sát bằng Zabbix. Phần AI thử nghiệm dùng Isolation Forest để phát hiện độ trễ khác thường.

**Mốc tài liệu: 09/11/2026, giờ Việt Nam.** Đây là hồ sơ phục vụ viết báo cáo và slide; cần đối chiếu trạng thái hiện hành trước khi kết luận nghiệm thu.

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
- AI còn ở trạng thái chờ đủ 30 mẫu trong nhật ký đã xem; chưa có bằng chứng mô hình đã đánh giá sau giai đoạn này.
- Item **Network AI report** đã xuất hiện trong Latest data; người dùng báo **Last value chưa có giá trị**. Luồng gửi báo cáo và widget chưa được nghiệm thu.

## Tệp hiện có

| Nhóm | Nguồn |
|---|---|
| Topology EVE-NG | [DoAn_HQ_BR1_BR2.unl](DoAn_HQ_BR1_BR2.unl) |
| FRR HQ / BR2 | [HQ_FRR.txt](HQ_FRR.txt), [BR2_FRR.txt](BR2_FRR.txt) |
| FRR BR1 và bản ghi terminal | [BR1.txt](BR1.txt), cần tách phần cấu hình khỏi log và ký tự điều khiển trước khi dùng |
| Snapshot interface, route, OSPF | [HQ_CHECK.txt](HQ_CHECK.txt), [BR1_check.txt](BR1_check.txt), [BR2_CHECK.txt](BR2_CHECK.txt) |
| Tài liệu Word cũ | [DoAn_EVE](DoAn_EVE), cần đọc nội dung trước khi tái sử dụng |
| Ảnh cũ | Hai tệp PNG ở thư mục gốc; chưa được phân tích trong lần bổ sung hồ sơ này |

Các snapshot không phải cấu hình lấy trực tiếp từ lab ngày 09/11. Không chạy nguyên tệp log BR1 vào shell. Không đưa credentials.json, mật khẩu, API token hoặc khóa riêng WireGuard vào repo.

## Việc ưu tiên

Xem lỗi gửi ai.report → xác nhận Last value có nội dung và thời gian mới → thêm widget Item history → thu đủ mẫu → kiểm thử độ trễ, mất gói và phục hồi → bổ sung minh chứng báo cáo.

Chưa có số đo để tuyên bố độ chính xác AI, thời gian hội tụ, mức giảm băng thông hoặc hiệu quả QoS.
