import json
import requests

s = requests.Session()
URL = "http://127.0.0.1/zabbix/api_jsonrpc.php"

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

token = None
try:
    with open("/opt/network-ai/credentials.json") as f:
        credentials = json.load(f)
    token = api("user.login", credentials)
    del credentials
    s.headers["Authorization"] = "Bearer " + token

    hosts = api("host.get", {
        "filter": {"host": ["Zabbix server"]},
        "output": ["hostid"]
    })
    if len(hosts) != 1:
        raise RuntimeError("Khong xac dinh duoc host Zabbix server")
    hostid = hosts[0]["hostid"]

    maps = api("valuemap.get", {
        "hostids": [hostid],
        "filter": {"name": ["Network AI state v1"]},
        "output": ["valuemapid"]
    })
    if maps:
        mapid = maps[0]["valuemapid"]
    else:
        labels = [
            "Bình thường",
            "Nghi ngờ bất thường",
            "Mất gói",
            "Mất kết nối",
            "Chờ dữ liệu",
            "Lỗi dữ liệu"
        ]
        result = api("valuemap.create", {
            "hostid": hostid,
            "name": "Network AI state v1",
            "mappings": [
                {"type": 0, "value": str(i), "newvalue": label}
                for i, label in enumerate(labels)
            ]
        })
        mapid = result["valuemapids"][0]

    existing = api("item.get", {
        "hostids": [hostid],
        "output": ["key_", "type", "value_type", "valuemapid"]
    })
    existing = {i["key_"]: i for i in existing}
    pending = []

    for router in ["HQ", "BR1", "BR2"]:
        for metric, title, datatype, unit in [
            ("state", "Status", 3, ""),
            ("rtt", "RTT", 0, "ms"),
            ("loss", "Packet loss", 0, "%")
        ]:
            key = f"ai.{metric}[{router}]"
            if key in existing:
                item = existing[key]
                if item["type"] != "2" or item["value_type"] != str(datatype):
                    raise RuntimeError("Item trung key nhung khac loai: " + key)
                if metric == "state" and item["valuemapid"] != mapid:
                    raise RuntimeError("Item state co value map khac: " + key)
                print("DA CO:", key)
                continue

            item = {
                "hostid": hostid,
                "name": f"AI {router} - {title}",
                "key_": key,
                "type": 2,
                "value_type": datatype,
                "units": unit,
                "history": "7d",
                "trends": "30d",
                "trapper_hosts": "127.0.0.1",
                "tags": [{"tag": "component", "value": "network-ai"}]
            }
            if metric == "state":
                item["valuemapid"] = mapid
            pending.append(item)

    if pending:
        result = api("item.create", pending)
        print("DA TAO:", len(result["itemids"]), "item")
    print("THANH CONG: da san sang cac item cho the AI.")
except Exception as e:
    print("LOI:", e)
    raise SystemExit(1)
finally:
    if token:
        try:
            api("user.logout", [])
        except Exception:
            pass
