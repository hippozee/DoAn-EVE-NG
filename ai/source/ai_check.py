import time
import getpass
import numpy as np
import requests
from sklearn.ensemble import IsolationForest

URL = "http://127.0.0.1/zabbix/api_jsonrpc.php"
HOSTS = {
    "R-HQ":  ["51181", "51182", "51183"],
    "R-BR1": ["51175", "51176", "51177"],
    "R-BR2": ["51178", "51179", "51180"],
}
MIN_SAMPLES = 30
s = requests.Session()

def api(method, params):
    r = s.post(URL, json={
        "jsonrpc": "2.0", "method": method,
        "params": params, "id": 1
    }, timeout=20)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]

def check(name, ids, items):
    print("\n---", name, "---")
    if any(i not in items for i in ids):
        print("THIEU ITEM: kiem tra lai cau hinh.")
        return

    rows = [items[i] for i in ids]
    now = int(time.time())
    if any(
        x["state"] != "0" or x["status"] != "0"
        or int(x["lastclock"]) == 0
        or abs(now - int(x["lastclock"])) > 180
        for x in rows
    ):
        print("DU LIEU CU/LOI: khong ket luan trang thai mang.")
        return

    ping, loss, rtt = [float(x["lastvalue"]) for x in rows]
    print(f"Ping={ping:.0f} | Loss={loss:.2f}% | RTT={rtt*1000:.3f} ms")

    if ping == 0:
        print("QUY TAC: MAT KET NOI")
        return
    if loss > 0:
        print("QUY TAC: CO MAT GOI")
        return

    history = api("history.get", {
        "output": ["clock", "value"],
        "history": 0,
        "itemids": [ids[2]],
        "time_from": now - 86400,
        "time_till": int(rows[2]["lastclock"]) - 1,
        "sortfield": "clock",
        "sortorder": "DESC",
        "limit": 500
    })
    values = [float(x["value"]) * 1000
              for x in history if float(x["value"]) > 0]
    print(f"So mau lich su RTT hop le: {len(values)}")

    if len(values) < MIN_SAMPLES:
        print(f"AI: CHO DU LIEU ({len(values)}/{MIN_SAMPLES} mau).")
        return
    if len(set(values)) < 5:
        print("AI: du lieu qua it bien thien, chua danh gia.")
        return

    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42,
        n_jobs=1
    )
    model.fit(np.array(values).reshape(-1, 1))
    current = np.array([[rtt * 1000]])
    label = int(model.predict(current)[0])
    score = float(model.decision_function(current)[0])
    status = "NGHI NGO BAT THUONG RTT" if label == -1 else "RTT BINH THUONG"
    print(f"AI: {status} | decision_score={score:.4f}")

token = None
try:
    import json
    with open("/opt/network-ai/credentials.json") as f:
        credentials = json.load(f)
    username = credentials["username"]
    password = credentials["password"]
    del credentials
    token = api("user.login", {
        "username": username, "password": password
    })
    del password
    s.headers["Authorization"] = "Bearer " + token

    ids = [i for group in HOSTS.values() for i in group]
    result = api("item.get", {
        "itemids": ids,
        "output": ["itemid", "lastvalue", "lastclock",
                   "state", "status"]
    })
    items = {x["itemid"]: x for x in result}
    for name, group in HOSTS.items():
        try:
            check(name, group, items)
        except Exception as e:
            print(name, "LOI:", e)
except Exception as e:
    print("LOI:", e)
finally:
    if token:
        try:
            api("user.logout", [])
        except Exception:
            pass
