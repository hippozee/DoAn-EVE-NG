# Mã AI lấy từ SERVER-ZABBIX — 10/11/2026

Đây là bản mã thực tế người dùng xuất từ VM trong gói `network-ai-backup-20261110-074327.tar.gz`, chuyển qua Base64 trong chat. Gói đã giải mã thành công: gzip CRC/kích thước và checksum mọi header tar đều đạt. Không chạy mã để truy cập VM trong bước đối chiếu này.

SHA-256 gói nhận được: `9a47762f46a446d3ba62e8f2bd289961dc40994892c38a9e6ac82b9ba6eeeacf`. Gói nén 6.718 byte, tar 51.200 byte. [Manifest](backup_manifest.json) ghi SHA-256 từng tệp theo đường dẫn gốc trong gói.

## Thành phần

| Tệp | Vai trò |
|---|---|
| [source/ai_check.py](source/ai_check.py) | Đọc API, kiểm tra dữ liệu, quy tắc ping/loss và Isolation Forest cho RTT |
| [source/publish_ai_cards.py](source/publish_ai_cards.py) | Chạy phân tích, ánh xạ trạng thái và gửi báo cáo cùng các item số qua zabbix_sender |
| [source/setup_ai_cards.py](source/setup_ai_cards.py) | Tạo value map và 9 item số; kiểm tra kiểu khi key đã tồn tại |
| [source/setup_login.py](source/setup_login.py) | Nhập thông tin đăng nhập trực tiếp trên VM, tạo credentials.json quyền 0600; không chứa mật khẩu thật |
| [systemd](systemd) | Service gốc, timer và drop-in publish.conf |
| [requirements.txt](requirements.txt) | Bản pip freeze được xuất từ venv; chưa thử cài lại toàn bộ trên môi trường sạch |

Mã, requirements và units được giữ nguyên nội dung từ gói hợp lệ. Không có credentials.json, venv, khóa riêng hoặc database trong gói. Không coi đây là snapshot toàn bộ VM.

## Luồng đang triển khai

Service gốc chạy ai_check.py; drop-in **network-ai-check.service.d/publish.conf** xóa ExecStart cũ rồi đặt:

~~~text
/opt/network-ai/venv/bin/python -u /opt/network-ai/publish_ai_cards.py
~~~

Timeout của service hợp nhất là 180 giây. Timer đặt OnBootSec=60s, OnUnitInactiveSec=60s; thời điểm thực tế còn phụ thuộc systemd và thời gian chạy. Publisher có timeout subprocess phân tích 90 giây và sender 20 giây.

AI đọc 9 ID item ICMP cố định của R-HQ/R-BR1/R-BR2 trên API local. Mã kiểm tra dữ liệu mới trong 180 giây, sau đó kiểm tra ping/loss. Khi kết nối tốt, mô hình fit lại trên tối đa 500 mẫu RTT dương trong 24 giờ, trước mẫu hiện tại; cần ít nhất 30 mẫu và 5 giá trị phân biệt.

Kết quả được lưu trên host kỹ thuật **Zabbix server**, trong ai.report và ai.state/ai.rtt/ai.loss cho từng router. Host lưu kết quả khác đối tượng mạng được phân tích. Batch thường có 10 giá trị; khi một router lỗi dữ liệu thì có thể chỉ gửi trạng thái cho router đó và số giá trị ít hơn 10.

Value map: 0 bình thường, 1 nghi ngờ bất thường RTT, 2 mất gói, 3 mất kết nối, 4 chờ dữ liệu, 5 lỗi dữ liệu. State là mã phân loại; decision_score không phải xác suất chính xác.

## Khôi phục: những gì cần có

1. Chuẩn bị SERVER-ZABBIX với API local, zabbix_sender và Python/venv phù hợp. Dùng requirements làm bản ghi phiên bản; việc dựng lại venv cần được thử riêng.
2. Đặt bốn tệp source vào /opt/network-ai. **Đối chiếu 9 ID item trong HOSTS với Zabbix đích**; ID khác hệ thống sẽ không tự ánh xạ theo tên.
3. Chạy setup_login.py tương tác trên VM để tạo credentials.json. Không đưa tệp đó lên Git.
4. Phải có item trapper text ai.report trên host Zabbix server, Allowed hosts 127.0.0.1. setup_ai_cards.py chỉ tạo 9 item số và value map, không tạo ai.report, host ICMP, template hay dashboard.
5. Chạy setup_ai_cards.py với tài khoản đủ quyền tạo item/value map. Tài khoản chỉ đọc không đủ cho bước thiết lập này.
6. Cài service/timer **kèm drop-in publish.conf** vào /etc/systemd/system, kiểm tra cấu hình hợp nhất bằng systemctl cat, daemon-reload, rồi kiểm tra chạy thủ công và processed/failed trước bật timer.
7. Tạo/khôi phục dashboard và trigger riêng: chúng chưa được export trong gói này.

Không chạy setup_login.py như một tác vụ định kỳ; chỉ dùng khi thiết lập thông tin đăng nhập. Không thay cả thư mục cấu hình từ một snapshot mà chưa đối chiếu với máy đích.

## Minh chứng và kiểm tra

- [Nhật ký gốc](../evidence/ai/2026-11-10/test-RTT-BR1.log): 12 báo cáo hoàn chỉnh từ 07:21:03 đến 07:33:40 UTC, mỗi lần sender processed 10, failed 0; cuối tệp có lần Starting 07:34:58 chưa có đầu ra trong cửa sổ thu.
- [CSV trích từ log](../evidence/ai/2026-11-10/observations.csv): 36 dòng router/báo cáo. report_time_utc là thời gian ghi báo cáo, không phải lastclock ICMP; các dòng lặp không chứng minh mẫu đo độc lập.
- [Kiểm tra offline](../evidence/ai/2026-11-10/validation.json): bốn tệp Python biên dịch cú pháp thành công; chỉ nạp hàm router_values để kiểm tra 8 tình huống tổng hợp và 36 khối router trong log, khớp trạng thái đã gửi. Chạy bằng Python 3.12.14 ở máy kiểm tra, không thực thi API/sender hoặc thay đổi VM.
- [T10 tăng RTT BR1](../docs/tests/T10_RTT_BR1_2026-11-10.md): một lần kiểm thử chức năng đã có kết quả. Test parser offline không thay thế thử mất gói, mất kết nối, dữ liệu cũ hoặc reboot trên lab.

## Giới hạn

Mô hình học lại mỗi lần, chưa có baseline khỏe cố định hoặc tập đánh giá có nhãn. RTT lịch sử chưa lọc đồng bộ theo ping/loss; sự cố kéo dài có thể đi vào tập học. ai_check.py bắt lỗi và có thể exit 0; publisher dùng nội dung từng khối để đưa state=5 khi nhận diện lỗi, nhưng sender nhận thành công không chứng minh kết quả mạng là bình thường. Khi publisher ngừng chạy hoàn toàn, các thẻ có thể giữ giá trị cuối; cần kiểm thử cảnh báo nodata.

Log 07:32:36 UTC còn ghi BR1 1,963 ms và BR2 1,829 ms bị gắn nhãn nghi ngờ ngoài đoạn đỉnh 107,667 ms. Chưa có ground truth cho các mẫu này, nên không tự tính đúng/sai hoặc độ chính xác.
