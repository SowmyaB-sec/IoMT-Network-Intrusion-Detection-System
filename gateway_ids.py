# Central Detection (CD) Engine with Rule-Based Anomaly Detection
# Receives telemetry from IoMT devices and applies real-time rule-based detection

import socket
import json
import threading
import time
import datetime
from collections import defaultdict, deque
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Storage: maintains last 100 samples per device for statistical baseline calculation
# Deque provides O(1) append and automatic eviction of old samples
history = defaultdict(lambda: deque(maxlen=100))
alerts = []

def detection_engine(device, data):
    """
    Core detection logic: applies 4 rule-based checks per device metric sample.
    Rules are tuned based on empirical baseline statistics (mean + 3σ for process anomalies).
    """
    h = history[device]
    h.append(data)
    
    # Wait for stable baseline: 20 samples = ~3 minutes at 10s intervals
    # Prevents false positives during system startup
    if len(h) < 20:
        return
    
    df = pd.DataFrame(h)
    cpu_mean, cpu_std   = df['cpu_percent'].mean(), df['cpu_percent'].std()
    proc_mean, proc_std = df['processes'].mean(), df['processes'].std()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Rule 1: CPU Exhaustion Attack Detection
    # Threshold: >85% CPU sustained across 3 consecutive samples (30s window)
    # Catches stress-ng, cryptominers, infinite loops
    if data['cpu_percent'] > 85 and len([x for x in list(h)[-3:] if x['cpu_percent'] > 85]) >= 3:
        msg = f"[{now}] CPU EXHAUSTION ATTACK → {device} ({data['cpu_percent']:.1f}%)"
        alerts.append(msg); print("\033[91m" + msg + "\033[0m")
    
    # Rule 2: Memory Depletion Attack Detection
    # Threshold: >90% memory usage in any single sample
    # Detects memory leaks, buffer overflows, malloc bombs
    if data['memory_percent'] > 90:
        msg = f"[{now}] MEMORY DEPLETION ATTACK → {device} ({data['memory_percent']:.1f}%)"
        alerts.append(msg); print("\033[91m" + msg + "\033[0m")
    
    # Rule 3: Process Injection / Fork Bomb Detection
    # Threshold: process count exceeds baseline mean + 3 standard deviations
    # Statistical anomaly detection catches sudden process spawning
    if data['processes'] > proc_mean + 3 * proc_std:
        msg = f"[{now}] PROCESS INJECTION ATTACK → {device} ({data['processes']} processes)"
        alerts.append(msg); print("\033[91m" + msg + "\033[0m")
    
    # Rule 4: Network Flood / DoS Detection
    # Threshold: >60 active connections (empirically tuned for IoMT device baseline)
    # Catches SYN floods, port scans, botnet C&C beaconing
    if data['net_connections'] > 60:
        msg = f"[{now}] NETWORK FLOOD / DoS DETECTED → {device} ({data['net_connections']} connections)"
        alerts.append(msg); print("\033[91m" + msg + "\033[0m")

def server():
    """
    TCP server thread: listens for JSON telemetry from MDA agents on port 9999.
    Each device sends metrics every 10 seconds (sampling period per Zachos et al. 2022).
    """
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 9999))
    s.listen(10)
    print("Gateway IDS listening on 192.168.56.1:9999 – waiting for IoMT devices...")
    
    while True:
        conn, _ = s.accept()
        raw = conn.recv(4096).decode()
        for line in raw.strip().split('\n'):
            if line:
                data = json.loads(line)
                print(f"Normal → {data['device']} | CPU {data['cpu_percent']}% | MEM {data['memory_percent']}%")
                detection_engine(data['device'], data)
        conn.close()

# Start TCP server in background thread
threading.Thread(target=server, daemon=True).start()

# Real-Time Visualization: 4-panel Plotly dashboard
# Updates every 8 seconds, displays last 100 samples per device
# Color-coded alerts in terminal (red = critical)
fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                    subplot_titles=('CPU %', 'Memory %', 'Processes', 'Active Connections'))

while True:
    fig.data = []  # Clear previous traces
    for dev, q in history.items():
        if len(q) > 1:
            df = pd.DataFrame(q)
            ts = pd.to_datetime(df['timestamp'])
            
            # Plot all 4 metrics per device
            fig.add_trace(go.Scatter(x=ts, y=df['cpu_percent'], name=f"{dev} CPU"), row=1, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['memory_percent'], name=f"{dev} MEM"), row=2, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['processes'], name=f"{dev} PROC"), row=3, col=1)
            fig.add_trace(go.Scatter(x=ts, y=df['net_connections'], name=f"{dev} NET"), row=4, col=1)
    
    fig.update_layout(height=950, title_text="IoMT Real-Time Intrusion Detection System (Rule-Based, No ML)")
    fig.show(renderer="browser")
    time.sleep(8)  # Dashboard refresh interval
