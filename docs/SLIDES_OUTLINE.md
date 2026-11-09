# Dàn ý 12 slide bảo vệ

Dàn ý này phục vụ tạo slide sau khi chốt dữ liệu. Gợi ý trình bày khoảng 10–12 phút, điều chỉnh theo yêu cầu giảng viên. Các chỗ chưa đủ minh chứng phải để nhãn chờ hoặc bỏ khỏi kết luận.

| Slide | Thông điệp chính | Hình/bảng cần có | Gợi ý lời nói và nguồn |
|---|---|---|---|
| 1. Đề tài | Mạng nhiều cơ sở, giám sát và AI thử nghiệm | Tên đề tài chính thức, tên SV/GV đã xác nhận | Nêu bài toán; không tự điền danh tính từ GitHub |
| 2. Bài toán | Kết nối HQ/BR1/BR2, giảm luồng trung chuyển, giám sát và bảo mật | 4 yêu cầu ngắn, tiêu chí kiểm thử | Giảm trung chuyển là mục tiêu; mức giảm cần đo |
| 3. Kiến trúc | Mô hình triển khai hiện tại dùng Linux/FRR | Topology thật từ .unl | Phân biệt router FRR, server Zabbix và VPC |
| 4. Định tuyến | OSPF chọn đường BR1–BR2 qua wg0 | Bảng cost và hai route đối xứng | Nêu snapshot [110/6], tránh nhầm metric Linux; CODEX_CONTEXT |
| 5. Bảo mật và quyền | Bảo mật đường chi nhánh và chính sách truy cập | Sơ đồ tunnel/underlay; ma trận firewall khi có | Có wg0 chưa đủ chứng minh handshake/mọi đường được mã hóa |
| 6. Giám sát | Zabbix có dữ liệu thật từ ba router | ICMP ping/loss/RTT cùng timestamp | Không dùng agent.ping time=0 để kết luận mất kết nối |
| 7. Luồng AI | Kiểm tra dữ liệu → quy tắc → ML RTT → báo cáo | Sơ đồ rẽ nhánh dữ liệu cũ, down/loss, đủ mẫu | Phân biệt rõ AI và ngưỡng/quy tắc |
| 8. Isolation Forest | Thử phát hiện độ trễ khác thường theo lịch sử | Input RTT, 30 mẫu tối thiểu, score và nhãn | 30 là ngưỡng demo; score không phải xác suất; ảnh hiện có 64/67/66 mẫu |
| 9. Vận hành tự động | systemd chạy và báo cáo được gửi về Zabbix | Nhật ký timer + giá trị report + widget | Đã có ảnh báo cáo thật trên AI Network Analysis; nêu sender là đường gửi hoạt động |
| 10. Kiểm thử mạng | Đường đi, lỗi và phục hồi có bằng chứng | Trước/trong/sau, route/packet loss/thời gian | Chưa có số thì trình bày kế hoạch, không trình bày như kết quả |
| 11. Đánh giá AI | Đánh giá tách tập khỏe và tình huống lỗi | Bảng TP/FP/TN/FN, score timeline nếu đã đo | Không gộp cảnh báo ping/loss bằng quy tắc vào thành tích ML |
| 12. Kết luận | Đã làm được gì, còn giới hạn gì | 3 kết quả có căn cứ, 3 việc cần cải thiện | Nói đúng trạng thái trong PROGRESS mới nhất |

## Trình tự demo sau khi các bước đã được nghiệm thu

1. Hiện topology và trạng thái bình thường.
2. Hiện route BR1–BR2 qua wg0; nếu cần chứng minh lưu lượng, đo từ đúng nguồn.
3. Hiện ICMP và báo cáo AI có timestamp mới.
4. Tạo một lỗi có kiểm soát trên đúng đường đo, đã chuẩn bị hoàn tác.
5. Hiện dữ liệu và kết quả phân tích, phân biệt nhánh quy tắc với nhánh ML.
6. Hoàn tác, kiểm tra route/dữ liệu/báo cáo phục hồi.

Không chọn thao tác tắt cổng nếu chưa có console và kế hoạch phục hồi. Không dùng một lần ping gián đoạn để tuyên bố độ chính xác mô hình.

## Câu hỏi nên chuẩn bị

- Vì sao dùng FRR thay cho Cisco? Trả lời theo môi trường thực tế và mục tiêu học, không tự gán lý do chi phí bản quyền.
- Vì sao BR1–BR2 không phải qua HQ? Chỉ next-hop và cost trong snapshot; cần đo để nói mức giảm tải.
- HQ có đặc quyền gì? Chỉ ra firewall/QoS đã kiểm thử; OSPF không tự tạo đặc quyền.
- Phần nào là AI? Isolation Forest trên RTT; mất kết nối/mất gói là quy tắc.
- Vì sao chọn 30 mẫu? Ngưỡng khởi động demo; chất lượng phải được đo trên dữ liệu riêng.
- Nếu dữ liệu cũ hoặc API lỗi? Không kết luận khỏe; báo lỗi dữ liệu và kiểm tra timestamp.
- AI có tự sửa mạng không? Bản hiện tại không tự thay đổi mạng.
- Vì sao chuyển sang sender? Bản history.push gặp lỗi Allowed hosts; sender buộc nguồn/đích local đã được nhận và widget hiển thị thật. Không nói đã sửa triệt để cấu hình nguồn frontend.

## Quy tắc biên tập

Mỗi slide một thông điệp, ưu tiên topology, bảng và ảnh thật. Không nhét toàn bộ log hoặc code lên slide. Chú thích thời điểm và nguồn; ảnh thí nghiệm đặt theo Test ID. Chỉ đưa số đã đo, giữ giới hạn rõ ràng, không ghi hoàn thành 100% khi còn mục chưa nghiệm thu.
