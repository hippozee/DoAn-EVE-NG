# Biên bản kiểm thử đồ án EVE-NG

**Ngày kiểm thử** 13/11/2026 · Giờ Việt Nam (UTC+7)

## Cấu hình trên lab

- HQ có VLAN 11 IT và VLAN 12 Nhân viên. Hai máy chủ nằm trong mạng 10.10.10.0/24.
- BR1 có VLAN 21 Kinh doanh, VLAN 22 Kế toán và VLAN 23 Kỹ thuật.
- BR2 có VLAN 31 Kinh doanh và VLAN 32 Kho.
- Mỗi VLAN phòng ban dùng mạng 10.10.<VLAN>.0/24 với gateway .1. Máy trạm kiểm thử tại BR1 và BR2 dùng .11.
- OSPF area 0 định tuyến giữa các site. Mỗi chi nhánh có một đường trực tiếp về HQ. WireGuard giữa hai chi nhánh cung cấp đường chuyển tiếp về HQ khi đường trực tiếp của một chi nhánh bị ngắt.

## QoS tại HQ

R-HQ phân lớp IPv4 theo dải IP nguồn chi nhánh trên cổng ens3, nơi hai luồng cùng đi vào LAN HQ. HTB đặt tổng băng thông thử nghiệm 10 Mbit/s. Cấu hình cuối cấp 7 Mbit/s cho BR1 và 3 Mbit/s cho BR2 khi cùng tranh chấp. Mỗi lớp có thể mượn phần còn dư đến 10 Mbit/s. Phép đo này kiểm tra chiều chi nhánh → LAN HQ.

Hai luồng UDP gửi khoảng 8 Mbit/s mỗi bên từ 10.10.21.1 và 10.10.31.1 tới 10.10.10.100. Mỗi kết quả tính trên 10 giây giao nhau sau 2 giây ổn định và chỉ tính tải hữu ích UDP.

| Chế độ | BR1 (Mbit/s) | BR2 (Mbit/s) |
|---|---:|---:|
| Đối chứng 5/5 | 4,792 | 4,786 |
| Ưu tiên BR1 7/3 | 6,761 | 2,897 |

Dịch vụ hq-qos.service trên R-HQ ở trạng thái enabled và active. Kiểm tra bằng systemctl status hq-qos và tc -s class show dev ens3.

## Demo Zabbix và AI

Chín item ICMP nguồn cập nhật mỗi 10 giây. Timer của mô-đun phân tích tiếp tục chạy định kỳ. Isolation Forest dùng tối thiểu 30 mẫu RTT và chỉ phát cảnh báo độ trễ khi điểm bất thường đi kèm RTT đạt ít nhất giá trị lớn hơn giữa 2 lần trung vị và trung vị cộng 5 ms. Mất phản hồi ICMP và mất gói được xử lý theo quy tắc.

| Giờ Việt Nam | Tình huống BR1 | Kết quả |
|---|---|---|
| 14:56:21 | Trạng thái nền | 1,550 ms, mất gói 0%, Bình thường (0) |
| 14:56:49 | Mô phỏng tăng 100 ms | 101,667 ms, mất gói 0%, điểm −0,3903, Nghi ngờ bất thường (1) |
| 14:57:20 | Gỡ độ trễ mô phỏng | 1,610 ms, Bình thường (0) |
| 14:57:58 | Mô phỏng mất phản hồi ICMP tới Zabbix | Ping 0, mất gói 100%, Mất kết nối (3) |
| 14:58:36 | Khôi phục phản hồi ICMP | 1,782 ms, mất gói 0%, Bình thường (0) |

HQ và BR2 cùng hiển thị Bình thường (0) ở lần kiểm tra cuối. Đã gỡ netem và luật chặn ICMP tạm. Đây là phép thử chức năng với một kịch bản được kiểm soát. Precision, recall và tỷ lệ báo động giả cần một tập mẫu có nhãn riêng.

[Dashboard AI Network Analysis](http://192.168.30.140/zabbix/zabbix.php?action=dashboard.view&dashboardid=403&from=now-15m&to=now)

## Kiểm tra hồi quy

- Ping từ gateway IT HQ tới máy Kinh doanh BR1 10.10.21.11 và máy Kho BR2 10.10.32.11. Mỗi đích trả lời 2/2 gói sau khi bật QoS.
- OSPF trên HQ hiển thị hai láng giềng FULL.
- Phiên kiểm thử VLAN trước đó đã xác nhận ping liên VLAN, failover riêng từng chi nhánh qua WireGuard, khôi phục WAN chính và bộ đếm firewall tăng khi chặn kết nối mới BR2 → BR1 và BR1 → Server HQ.
