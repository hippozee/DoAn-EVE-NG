# Kế hoạch kiểm thử và thu minh chứng

Đây là kế hoạch, không phải bảng kết quả đã đạt. Snapshot route và một giá trị ping không thay thế phép thử có thời gian, điều kiện và log.

## Chuẩn bị

- Đối chiếu interface thực tế bằng ip -br a, ip route, OSPF và topology hiện tại.
- Dùng console EVE-NG sẵn sàng để phục hồi trước thử nghiệm làm gián đoạn.
- Lưu bản cấu hình trước thử, đánh dấu thời gian và múi giờ.
- Chỉ thay đổi một yếu tố mỗi lần. Không làm gián đoạn phiên truy cập quản trị duy nhất.
- Thu baseline khỏe; với kiểm thử AI cần mô hình đã học và tập đánh giá tách thời gian.
- Không giảm MIN_SAMPLES chỉ để hiển thị nhãn AI.

## Ma trận

| ID | Tình huống | Cách quan sát và tiêu chí | Trạng thái |
|---|---|---|---|
| T01 | OSPF bình thường | Neighbor Full; tuyến và next-hop phù hợp từng node | Có snapshot cũ; cần tái kiểm tra |
| T02 | ICMP HQ/BR1/BR2 | Giá trị mới, ping=1; ghi loss và RTT | Đã thấy ảnh 09/11; chưa có chuỗi CSV |
| T03 | BR1↔BR2 ưu tiên wg0 | ip route get và traceroute/traffic tại hai đầu; route qua wg0 | Có route snapshot; chưa đủ phép đo lưu lượng |
| T04 | Xác nhận tunnel | wg show có handshake mới và counters tăng khi truyền thử | Chưa có minh chứng trong bộ docs |
| T05 | Mất đường trực tiếp BR1–BR2 | Tạo lỗi có kiểm soát sau khi xác định interface; ghi next-hop trước/sau, packet loss, thời gian phục hồi qua HQ | Chờ thực hiện và log |
| T06 | Phục hồi đường trực tiếp | Hoàn tác chính thay đổi T05; route quay lại như thiết kế, traffic ổn định | Chờ |
| T07 | Chính sách BR→HQ | Từ máy thuộc LAN chi nhánh, thử đúng dịch vụ cho phép/bị chặn; ghi firewall counters | Chờ ruleset và ma trận quyền |
| T08 | QoS khi có tải | Hai luồng cạnh tranh có nhãn/DSCP rõ; đo throughput, RTT, loss trước/sau | Chờ cấu hình và kết quả đọc được |
| T09 | AI đủ mẫu bình thường | Mỗi host đủ mẫu, có điểm mô hình, ghi tỷ lệ cảnh báo nhầm trên tập khỏe | Đã đủ mẫu/có score; chưa đo cảnh báo nhầm |
| T10 | RTT tăng có kiểm soát | Gây độ trễ trên đúng đường Zabbix đo; lưu thời điểm, RTT và score trước/trong/sau | Đạt chức năng trong một lần thử BR1 ngày 10/11; xem [kết quả](tests/T10_RTT_BR1_2026-11-10.md), chưa đánh giá độ chính xác |
| T11 | Mất gói | Gây loss có kiểm soát trên đường đo; kiểm tra nhánh quy tắc, không gọi là phát hiện ML | Chờ |
| T12 | Mất kết nối | Ping mới bằng 0 và báo quy tắc mất kết nối; phân biệt lỗi thu thập | Chờ |
| T13 | Dữ liệu cũ/API lỗi | Phải báo lỗi hoặc dữ liệu cũ, không hiển thị kết luận khỏe | Chờ |
| T14 | Gửi báo cáo/dashboard | zabbix_sender nhận đủ một giá trị; widget có timestamp/nội dung mới | Đã xác nhận gửi thật và widget AI Network Analysis |
| T15 | Tự khởi động | Sau reboot có timer và báo cáo mới; không nhập mật khẩu thủ công | Chưa kiểm thử reboot |

## Lệnh đọc cấu hình và trạng thái

Trên router Linux/FRR:

```bash
ip -br a
ip route
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route"
vtysh -c "show running-config"
```

Trên BR1/BR2 khi có WireGuard:

```bash
wg show
```

Xuất ip route get cho một đích LAN phù hợp để biết đường đi thực tế. Muốn kết luận lưu lượng máy trạm đi đường nào phải đo từ đúng máy/địa chỉ nguồn, không chỉ từ router.

Chỉ bổ sung lệnh gây lỗi sau khi đã chốt interface, chiều lưu lượng và lệnh phục hồi tương ứng. Không dùng tên ens4/ens6 từ snapshot để tắt ngay một cổng đang quản trị.

## Mẫu ghi kết quả cho mỗi lần thử

| Trường | Nội dung cần ghi |
|---|---|
| Run ID / Test ID | Ví dụ RUN-YYYYMMDD-01 / T10 |
| Topology và cấu hình | Commit nguồn, khác biệt so với lab, phiên bản |
| Thời gian | Thời điểm bắt đầu/kết thúc, UTC hoặc +07:00 nhất quán |
| Điểm đo | Máy nguồn, máy đích, đường Zabbix thực sự đi qua |
| Baseline | Khoảng thời gian, số mẫu, phân bố RTT/loss |
| Tác động | Thay đổi chính xác, thời điểm áp dụng |
| Kỳ vọng | Viết trước khi quan sát kết quả |
| Kết quả | Route, ping/loss, score, trạng thái, timestamp |
| Phục hồi | Thay đổi hoàn tác, kiểm tra sau phục hồi |
| Bằng chứng | Đường dẫn ảnh/log/CSV và mô tả |
| Đạt/không đạt | Nêu tiêu chí và hạn chế |

Cột CSV đề xuất: run_id,test_id,timestamp,host,ping,loss_pct,rtt_ms,ai_label,decision_score,ground_truth,phase,model_id.

## Đánh giá AI

Gắn nhãn thực nghiệm độc lập với kết quả mô hình. Tách dữ liệu học và đánh giá theo thời gian, không để sự cố đánh giá lọt vào baseline. Với mẫu đủ căn cứ, báo cáo TP/FP/TN/FN, precision/recall/F1, tỷ lệ cảnh báo nhầm và độ trễ phát hiện. Khi mẫu ít, trình bày số đếm và phạm vi thí nghiệm; không tuyên bố tổng quát hóa cho mạng doanh nghiệp.

Không gộp T11/T12 là bằng chứng độ chính xác Isolation Forest vì hai nhánh đó sử dụng quy tắc.
