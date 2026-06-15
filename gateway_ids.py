# gateway_ids.py – Central Detection Engine (Completes Zachos et al. 2022)
import socket, json, threading, time, datetime
from collections import defaultdict, deque
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"

history = defaultdict(lambda: deque(maxlen=300))

def detection_engine(device, data):
    h = history[device]
    h.append(data)
    if len(h) < 20: return
    df = pd.DataFrame(h)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    if data['cpu_percent'] > 85 and len([x for x in list(h)[-3:] if x['cpu_percent'] > 85]) >= 3:
        print(f"\033[91m[{now}] CPU EXHAUSTION ATTACK → {device} ({data['cpu_percent']:.1f}%)\033[0m")
    if data['memory_percent'] > 90:
        print(f"\033[91m[{now}] MEMORY DEPLETION ATTACK → {device} ({data['memory_percent']:.1f}%)\033[0m")
    if data['processes'] > df['processes'].mean() + 3*df['processes'].std():
        print(f"\033[91m[{now}] PROCESS INJECTION → {device} ({data['processes']} procs)\033[0m")
    if data['net_connections'] > 60:
        print(f"\033[91m[{now}] NETWORK FLOOD → {device} ({data['net_connections']} conns)\033[0m")

def server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 9999))
    s.listen()
    print("Gateway listening on 192.168.56.1:9999")
    while True:
        conn, _ = s.accept()
        raw = conn.recv(8192).decode()
        for line in raw.strip().split('\n'):
            if line:
                data = json.loads(line)
                print(f"Normal → {data['device']} | CPU {data['cpu_percent']}%")
                detection_engine(data['device'], data)
        conn.close()

threading.Thread(target=server, daemon=True).start()

while True:
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=('CPU %', 'Memory %', 'Processes', 'Active Connections'))
    for dev in history:
        if len(history[dev]) > 5:
            df = pd.DataFrame(history[dev])
            ts = pd.to_datetime(df['timestamp'])
            fig.add_trace(go.Scatter(x=ts, y=df['cpu_percent'], name=f"{dev} CPU"), row=1, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['memory_percent'], name=f"{dev} MEM"), row=2, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['processes'], name=f"{dev} PROC"), row=3, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['net_connections'], name=f"{dev} NET"), row=4, col=1)
    fig.update_layout(height=1000, title_text="IoMT Real-Time IDS – Zachos et al. 2022 Extension")
    fig.show()
    time.sleep(8)
