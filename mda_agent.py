# Monitoring & Data Acquisition (MDA) Agent
# Collects system metrics from IoMT devices and transmits to central gateway
# Designed for resource-constrained devices (low CPU/memory overhead)

import time
import json
import socket
import psutil
import datetime
import os

# Gateway connection settings
GATEWAY_IP   = "192.168.56.1"
GATEWAY_PORT = 9999

# Device identification: uses hostname (e.g., HeartMonitor, GlucoseSensor)
DEVICE_NAME  = os.uname().nodename.strip()

while True:
    # Collect telemetry snapshot using psutil (cross-platform system monitoring)
    payload = {
        "timestamp":        datetime.datetime.now().isoformat(),
        "device":           DEVICE_NAME,
        "cpu_percent":      round(psutil.cpu_percent(interval=1), 2),
        "memory_percent":   round(psutil.virtual_memory().percent, 2),
        "processes":        len(psutil.pids()),
        "net_connections":  len(psutil.net_connections())
    }
    
    try:
        # Send JSON telemetry to gateway via TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((GATEWAY_IP, GATEWAY_PORT))
        sock.sendall((json.dumps(payload) + "\n").encode())
        sock.close()
    except Exception as e:
        # Silent retry if gateway not ready or network unreachable
        # Prevents log spam on agent devices with limited storage
        pass
    
    # Sampling interval: 10 seconds (per Zachos et al. 2022 architecture)
    time.sleep(10)
