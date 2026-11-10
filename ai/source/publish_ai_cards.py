import sys
import re
import json
import math
import shutil
import subprocess
from datetime import datetime

def router_values(router, text):
    match = re.search(
        rf"(?ms)^--- R-{router} ---[ \t]*\n(.*?)(?=^--- R-|\Z)",
        text
    )
    block = match.group(1) if match else ""
    state = 5

    if block and not any(x in block for x in [
        "THIEU ITEM", "DU LIEU CU/LOI", "LOI:"
    ]):
        if "QUY TAC: MAT KET NOI" in block:
            state = 3
        elif "QUY TAC: CO MAT GOI" in block:
            state = 2
        elif "CHO DU LIEU" in block or "chua danh gia" in block:
            state = 4
        elif "AI: NGHI NGO BAT THUONG RTT" in block:
            state = 1
        elif "AI: RTT BINH THUONG" in block:
            state = 0

    metrics = re.search(
        r"Ping=(\d+) \| Loss=([\d.]+)% \| RTT=([\d.]+) ms",
        block
    )
    values = []
    if state != 5 and metrics:
        ping = int(metrics.group(1))
        loss = float(metrics.group(2))
        rtt = float(metrics.group(3))
        if (ping in (0, 1) and math.isfinite(loss)
                and math.isfinite(rtt) and 0 <= loss <= 100
                and rtt >= 0):
            values += [
                (f"ai.rtt[{router}]", rtt),
                (f"ai.loss[{router}]", loss)
            ]
        else:
            state = 5
    else:
        state = 5

    values.append((f"ai.state[{router}]", state))
    print(f"{router}: state={state}", flush=True)
    return values

def main():
    sender = shutil.which("zabbix_sender")
    if not sender:
        raise RuntimeError("Khong tim thay zabbix_sender")

    ai = subprocess.run(
        [sys.executable, "/opt/network-ai/ai_check.py"],
        capture_output=True, text=True, timeout=90
    )
    if ai.returncode != 0:
        raise RuntimeError(ai.stderr[-1500:])
    if not ai.stdout.strip():
        raise RuntimeError("AI khong tra ket qua")

    report = (
        "NETWORK AI REPORT\nUpdated: "
        + datetime.now().astimezone().isoformat(timespec="seconds")
        + "\n" + ai.stdout
    )
    print(report, flush=True)
    values = [("ai.report", report)]

    for router in ["HQ", "BR1", "BR2"]:
        values += router_values(router, ai.stdout)

    payload = "\n".join(
        '"Zabbix server" ' + key + " "
        + json.dumps(str(value), ensure_ascii=False)
        for key, value in values
    ) + "\n"

    result = subprocess.run(
        [sender, "-z", "127.0.0.1", "-I", "127.0.0.1",
         "-t", "10", "-i", "-"],
        input=payload, capture_output=True,
        encoding="utf-8", timeout=20
    )
    print(result.stdout, flush=True)
    expected = rf"processed:\s*{len(values)};\s*failed:\s*0;"
    if result.returncode != 0 or not re.search(expected, result.stdout):
        raise RuntimeError("Gui that bai: " + result.stderr)

    print("THANH CONG: DA GUI DU LIEU CHO CAC THE AI", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("LOI:", e, flush=True)
        sys.exit(1)
