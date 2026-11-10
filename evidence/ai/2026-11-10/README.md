# Minh chứng AI — ngày 10/11/2026

- [test-RTT-BR1.log](test-RTT-BR1.log): tệp journal gốc, giữ nguyên byte từ gói hợp lệ; cửa sổ yêu cầu 07:20–07:35 UTC (14:20–14:35 Việt Nam). Đầu tệp là lần Starting 07:21:02, có 12 báo cáo đầy đủ, cuối tệp là Starting 07:34:58 chưa có đầu ra trong phần thu này. Không suy lần chạy cuối thất bại.
- [observations.csv](observations.csv): 36 dòng trích từ 12 báo cáo, ba router mỗi báo cáo. report_time_utc là timestamp journal lúc in báo cáo, process_id phân biệt lần chạy. Không có lastclock hay ID mẫu ICMP; không coi mọi dòng là một phép đo độc lập.
- [validation.json](validation.json): kết quả kiểm tra offline. Chỉ nạp AST của hàm router_values, không chạy chương trình phân tích, API login hoặc zabbix_sender. Dữ liệu tổng hợp kiểm tra 0/1/2/3/4/5, thiếu khối và loss ngoài 0–100%; không thay thế kiểm thử mạng thực.

CSV giữ nguyên độ chính xác hiển thị trong log: RTT ba chữ số, score bốn chữ số thập phân. Không tái tính mô hình từ CSV vì không có toàn bộ lịch sử dùng để fit.

Log chứng minh kết quả ứng dụng và sender tại các lần chạy, không chứa lệnh tc, log timer rollback, export dashboard hoặc toàn bộ lịch sử ICMP. Xem [T10](../../../docs/tests/T10_RTT_BR1_2026-11-10.md) cho kết luận và giới hạn.

Nguồn và hash: [ai/README.md](../../../ai/README.md), [manifest](../../../ai/backup_manifest.json). Ảnh đang được lưu trong chat, chưa có tệp ảnh trong thư mục này.
