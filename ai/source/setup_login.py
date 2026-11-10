from pathlib import Path
import getpass
import json
import os
import shutil

path = Path("/opt/network-ai/ai_check.py")
text = path.read_text()

old = '''    username = input("Tai khoan Zabbix [Admin]: ").strip() or "Admin"
    password = getpass.getpass("Mat khau Zabbix: ")'''

new = '''    import json
    with open("/opt/network-ai/credentials.json") as f:
        credentials = json.load(f)
    username = credentials["username"]
    password = credentials["password"]
    del credentials'''

if old not in text and new not in text:
    raise SystemExit("Ma nguon khac du kien. Gui anh loi nay.")

username = input("Tai khoan Zabbix [Admin]: ").strip() or "Admin"
password = getpass.getpass("Mat khau Zabbix: ")

config = "/opt/network-ai/credentials.json"
fd = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.fchmod(fd, 0o600)
with os.fdopen(fd, "w") as f:
    json.dump({"username": username, "password": password}, f)
del password

if old in text:
    backup = path.with_name("ai_check.manual.bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_text(text.replace(old, new, 1))

print("THANH CONG: da cau hinh dang nhap tu dong.")
