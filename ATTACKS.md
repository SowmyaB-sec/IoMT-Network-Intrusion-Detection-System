# Attack Simulation Guide

This guide demonstrates how to trigger each of the four detection rules using standard penetration testing tools.

⚠️ **Warning**: Only run these attacks in the isolated VirtualBox testbed. Never on production systems.

---

## Prerequisites

- Gateway IDS must be running (`gateway_ids.py`)
- Both MDA agents must be active (HeartMonitor, GlucoseSensor)
- Dashboard showing green baseline metrics

---

## Attack 1: CPU Exhaustion

**Target**: Detect cryptominers, infinite loops, CPU-intensive malware

**Command** (run on IoMT-HeartMonitor):
```bash
stress-ng --cpu 8 --cpu-method all --timeout 120s
```

**Parameters:**
- `--cpu 8`: Spawn 8 CPU stressor processes
- `--cpu-method all`: Use all available stress methods
- `--timeout 120s`: Run for 2 minutes

**Expected Behavior:**
- CPU % graph spikes to ~100%
- After 30 seconds (3 samples), terminal shows:
```
[14:23:17] CPU EXHAUSTION ATTACK → IoMT-HeartMonitor (98.4%)
```
- Dashboard shows red line on CPU graph

**Detection Rule:**
```
IF cpu_percent > 85% for 3 consecutive samples (30s window)
THEN trigger alert
```
---

## Attack 2: Memory Depletion

**Target**: Detect buffer overflows, memory leaks, malloc bombs

**Command** (run on IoMT-GlucoseSensor):
```bash
timeout 120 python3 - <<'PY'
import time
x = []
print("Memory leak attack started...")
while True:
    x.append("X" * 100000)  # Allocate ~100KB per iteration
    time.sleep(0.05)
PY
```

**How it works:**
- Rapidly appends large strings to a list
- Memory usage climbs ~20MB/second
- Triggers alert when >90% memory consumed

**Expected Behavior:**
- Memory % graph climbs steadily
- Terminal shows (usually within 15-30 seconds):
```
[14:25:43] MEMORY DEPLETION ATTACK → IoMT-GlucoseSensor (93.2%)
```
- Dashboard shows red spike on Memory graph

**Detection Rule:**
```
IF memory_percent > 90% in any sample
THEN trigger alert
```
**Stop attack manually if needed:**
```bash
pkill -f "python3 -"
```

---

## Attack 3: Process Injection / Fork Bomb

**Target**: Detect malicious process spawning, backdoor installation

**Command** (run on IoMT-HeartMonitor):
```bash
timeout 120 bash -c '
for i in {1..400}; do
    sleep 3600 &  # Spawn background process sleeping for 1 hour
done
echo "Created 400+ background processes"
'
```

**How it works:**
- Creates 400 harmless background processes
- Simulates fork bomb or process injection attack
- Safe version (timeout ensures cleanup)

**Expected Behavior:**
- Process count graph jumps from ~150 → ~550
- Terminal shows:
```
[14:28:09] PROCESS INJECTION ATTACK → IoMT-HeartMonitor (552 processes)
```
- Dashboard shows sudden spike on Processes graph

**Detection Rule:**
```
IF processes > baseline_mean + 3 * standard_deviation
THEN trigger alert
```
**Cleanup** (if needed):
```bash
pkill -f "sleep 3600"
```

---

## Attack 4: Network Flood / DDoS

**Target**: Detect SYN floods, port scans, botnet traffic

**Command** (run on IoMT-GlucoseSensor):
```bash
sudo hping3 --flood -S 192.168.56.1 -p 80
```

**Parameters:**
- `--flood`: Send packets as fast as possible
- `-S`: SYN flag (simulates TCP handshake flood)
- `192.168.56.1`: Target gateway
- `-p 80`: Target port (HTTP)

**Expected Behavior:**
- Active Connections graph surges to 100+
- Terminal shows (within 10-20 seconds):
```
[14:30:22] NETWORK FLOOD / DoS DETECTED → IoMT-GlucoseSensor (124 connections)
```
- Dashboard shows red spike on Network graph

**Detection Rule:**
```
IF net_connections > 60
THEN trigger alert
```
**Stop attack:**
```
Press Ctrl+C in the hping3 terminal
```
---

## Full Attack Sequence

To demonstrate all four detection capabilities:

```bash
# 1. Start on HeartMonitor
ssh iomt@192.168.56.101
stress-ng --cpu 8 --timeout 60s

# Wait 60 seconds, then:
timeout 60 bash -c 'for i in {1..400}; do sleep 3600 & done'

# 2. Start on GlucoseSensor
ssh iomt@192.168.56.102
timeout 60 python3 -c "import time; x=[]; [x.append('X'*100000) or time.sleep(0.05) for _ in iter(int, 1)]"

# Wait 60 seconds, then:
sudo hping3 --flood -S 192.168.56.1 -p 80
```

**Timeline:**
- **0:00-1:00**: CPU attack on HeartMonitor
- **1:00-2:00**: Process injection on HeartMonitor
- **2:00-3:00**: Memory attack on GlucoseSensor
- **3:00-4:00**: Network flood from GlucoseSensor

---

## Validation Checklist

After running all attacks, verify:

- [ ] 4 distinct red alerts in terminal
- [ ] All 4 graphs show attack spikes
- [ ] Dashboard auto-refreshes every 8 seconds
- [ ] No false positives during 15-min baseline before attacks
- [ ] Metrics return to normal after attacks end

---

## Detection Metrics

| Attack | Detection Time | Threshold Exceeded |
|--------|---------------|-------------------|
| CPU Exhaustion | ~30 seconds | >85% for 3 samples |
| Memory Depletion | ~10-20 seconds | >90% instantly |
| Process Injection | ~10 seconds | >mean + 3σ |
| Network Flood | ~10-20 seconds | >60 connections |

---

## Safety Notes

1. **Run only in VirtualBox testbed** - These are real attacks that can crash systems
2. **CPU attacks may slow VMs** - Normal behavior; use `--cpu 2` if VM becomes unresponsive
3. **hping3 requires root** - Use `sudo` for network flood attack
4. **Timeout commands auto-cleanup** - All attacks self-terminate after 60-120 seconds
5. **Reboot VMs if needed** - Clears all attack artifacts

---

## Troubleshooting

### Attack not detected?
```bash
# Check baseline is established (need 20+ samples = 3+ minutes)
# Verify agent is sending data:
ps aux | grep mda_agent

# Check gateway is receiving:
sudo tcpdump -i enp0s3 port 9999
```

### False positives?
- Adjust thresholds in `gateway_ids.py` detection rules
- Extend baseline period (increase 20 samples → 40 samples)
- Check for resource contention on host machine

### VM becomes unresponsive during attack?
- Reduce attack intensity (`--cpu 2` instead of `--cpu 8`)
- Allocate more RAM to VM (4GB → 6GB)
- Close other applications on host
