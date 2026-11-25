# Flow IDS trên SERVER-ZABBIX — 25/11/2026

Random Forest chạy trên SERVER-ZABBIX với scikit-learn 1.9.1. Mô hình dùng 5 đặc trưng gồm thời lượng, số gói và tổng số byte theo hai chiều của luồng. Ngưỡng 0,15 được chọn theo F1 trên tập thứ Năm. Chương trình coi mọi nhãn khác BENIGN là ATTACK và loại các vector đặc trưng trùng giữa các tập.

Nguồn là 8 tệp CSV thuộc CICIDS2017, công bố bởi Đại học New Brunswick và tải từ bản sao trên Hugging Face. [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) · [Bản CSV](https://huggingface.co/datasets/muzom/CIC-IDS2017/tree/main)

Số vector hợp lệ sau lọc là 1.133.034 ở tập học (thứ Hai đến thứ Tư), 249.509 ở tập xác thực (thứ Năm) và 399.485 ở tập kiểm thử (thứ Sáu).

| Chỉ số | Xác thực | Kiểm thử |
|---|---:|---:|
| Bình thường, dự đoán bình thường (TN) | 246.365 | 268.912 |
| Bình thường, bị báo nhầm (FP) | 1.126 | 941 |
| Tấn công, bị bỏ sót (FN) | 1.971 | 48.001 |
| Tấn công, được phát hiện (TP) | 47 | 81.631 |
| Precision | 4,01% | 98,86% |
| Recall | 2,33% | 62,97% |
| F1 | 0,0295 | 0,7694 |
| Tỷ lệ báo nhầm | 0,455% | 0,349% |

Chênh lệch recall giữa hai ngày cho thấy hiệu năng thay đổi mạnh theo tập lưu lượng. Trong 48.001 luồng tấn công bị bỏ sót ở tập thứ Sáu, 45.889 mang nhãn DDoS, 926 PortScan và 1.186 Bot.

## Kiểm thử chuyển dữ liệu sang Zabbix

Lệnh suy luận đọc lại tệp `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`, ghi nhận 225.743 luồng hợp lệ, 2 dòng lỗi và 82.186 luồng vượt ngưỡng. Lần chạy này dùng toàn bộ tệp riêng lẻ để kiểm tra tích hợp, nên số luồng được đếm theo dòng CSV. `zabbix_sender` trả về `processed: 2; failed: 0`. Hai thẻ Benchmark trên [dashboard Flow IDS](http://192.168.30.140/zabbix/zabbix.php?action=dashboard.view&dashboardid=404) hiển thị kết quả đã xác minh.

Hai thẻ Lab đang chờ nguồn luồng trực tiếp. Trước khi bật cảnh báo live, cần chọn điểm thu tại HQ, kiểm tra đặc trưng trích xuất khớp với dữ liệu học và đánh giá lại mô hình trên lưu lượng lab. Dịch vụ Zabbix và timer giám sát RTT cũ đều ở trạng thái active sau thử nghiệm.

## Vị trí trên SERVER-ZABBIX

Mã nguồn và kết quả nằm trong `/opt/network-ids`, gồm `flow_ids.py`, `model.joblib`, `training.log`, `benchmark.log` và `data/`.

SHA-256 của `model.joblib`

```text
d51fca9ee623b27f68ecf927d6298c9ca4b0e687df4c81a0a907186157c7ce6b
```
