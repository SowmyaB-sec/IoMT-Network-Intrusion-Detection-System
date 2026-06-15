# mda_agent.py – Monitoring & Data Acquisition Agent (Zachos et al. 2022)
import time, socket, json, psutil, datetime, os

DEVICE = os.uname().nodename
GATEWAY_IP = "192.168.56.1"
GATEWAY_PORT = 9999

while True:
    data = {
        "device": DEVICE,
        "timestamp": datetime.datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "processes": len(psutil.pids()),
        "net_connections": len(psutil.net_connections())
    }
    try:
        s = socket.socket()
        s.connect((GATEWAY_IP, GATEWAY_PORT))
        s.sendall((json.dumps(data) + "\n").encode())
        s.close()
    except:
        pass
    time.sleep(10)
