# IoMT Intrusion Detection System
*A lightweight, rule-based anomaly detection system for resource-constrained Internet of Medical Things networks*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

This project implements a **real-time intrusion detection system (IDS)** for Internet of Medical Things (IoMT) networks. Unlike traditional ML-based solutions that require heavy computation, this system uses **explainable rule-based detection** that runs on resource-constrained devices.

The system detects four critical attack types:
- **CPU Exhaustion** (cryptominers, infinite loops)
- **Memory Depletion** (buffer overflows, memory leaks)
- **Process Injection** (fork bombs, malicious spawning)
- **Network Floods** (SYN floods, DDoS attacks)

### Key Features

✅ **100% Detection Rate** across all tested attack vectors  
✅ **Zero False Positives** during extended baseline monitoring  
✅ **Low Overhead**: <5% CPU usage on gateway  
✅ **Real-Time Dashboard**: 4-panel Plotly visualization with color-coded alerts  
✅ **Explainable Rules**: No black-box ML—every alert has a clear threshold  

---

## Architecture
<img width="715" height="596" alt="ARCHITECTURE diagram" src="https://github.com/user-attachments/assets/5ea28573-f0b7-4a48-8a02-1aa410fa4ecf" />

### System Components

1. **MDA Agents** (`mda_agent.py`): Lightweight monitoring daemons running on IoMT devices
   - Collects CPU, memory, process, and network metrics using `psutil`
   - Transmits JSON payloads every 10 seconds
   - Minimal resource footprint

2. **Central Detection Engine** (`gateway_ids.py`): Gateway-based rule processor
   - Receives telemetry via TCP socket server
   - Applies 4 statistical + threshold-based rules
   - Triggers color-coded terminal alerts
   - Renders real-time 4-panel dashboard

---

## Detection Rules

| Attack Type | Rule | Threshold |
|------------|------|-----------|
| CPU Exhaustion | Sustained high CPU | >85% for 3 consecutive samples (30s) |
| Memory Depletion | Instant memory spike | >90% in any single sample |
| Process Injection | Statistical anomaly | Process count > mean + 3σ |
| Network Flood | Connection surge | >60 active connections |

**Why These Thresholds?**
- Tuned empirically from 15-minute baseline monitoring
- Balance between sensitivity (catching attacks) and specificity (avoiding false alarms)
- Designed for IoMT devices with typical load: <20% CPU, <50% memory, <100 processes

---

## Results

| Metric | Value |
|--------|-------|
| **Detection Rate** | 100% (4/4 attacks detected) |
| **False Positive Rate** | 0% |
| **Average Latency** | 14.2 seconds (9.7s - 16.4s range) |
| **Gateway CPU Overhead** | <5% |
| **Baseline Stability** | 0 false alerts across 6+ hours |

---

## Quick Start

### Prerequisites

- **Hardware**: 16GB RAM, 50GB disk space (for VirtualBox VMs)
- **Software**: 
  - Oracle VirtualBox 7.0+
  - Ubuntu 22.04 LTS
  - Python 3.8+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/iomt-ids.git
cd iomt-ids
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Set up testbed** (see [SETUP.md](docs/SETUP.md) for detailed VM configuration)

4. **Run the system**

On gateway VM:
```bash
python3 gateway_ids.py
```

On each IoMT device VM:
```bash
nohup python3 mda_agent.py > /dev/null 2>&1 &
```

5. **Simulate attacks** (see [ATTACKS.md](docs/ATTACKS.md) for full attack guide)

---

## Project Structure
```
iomt-ids/
├── gateway_ids.py          # Central detection engine + dashboard
├── mda_agent.py            # Device-side monitoring agent
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── docs/
│   ├── SETUP.md           # Testbed configuration guide
│   ├── ATTACKS.md         # Attack simulation commands
│   └── ARCHITECTURE.md    # Technical deep-dive
└── screenshots/
├── dashboard_normal.png
├── attack_cpu.png
├── attack_memory.png
├── attack_process.png
└── attack_network.png
```

---

## Technical Background

This project extends the work of **Zachos et al. (2022)**, who proposed a hybrid IDS architecture for IoMT but only implemented the data collection component (MDA). This implementation:

1. ✅ Completes the **Central Detection (CD) engine** with rule-based logic
2. ✅ Adds **real-time visualization** for security operators
3. ✅ Validates detection accuracy against **four attack vectors**
4. ✅ Measures **latency and overhead** in a realistic testbed

### Why Rule-Based Instead of ML?

IoMT devices are **resource-constrained** (limited CPU, memory, battery). Machine learning models:
- Require GPU/high-end CPU for inference
- Lack explainability (black-box decisions)
- Need constant retraining as device behavior evolves

**Rule-based detection** provides:
- ✅ Explainable alerts (every threshold has a reason)
- ✅ Minimal computational overhead (<5% CPU)
- ✅ No training data required
- ✅ Instant deployment

---

## Limitations & Future Work

**Current Limitations:**
- Virtual testbed (not tested on physical IoT hardware)
- Small network scale (2 devices)
- No encryption/authentication on telemetry channel
- Static thresholds (no adaptive learning)

**Planned Improvements:**
- [ ] Deploy on Raspberry Pi / real medical devices
- [ ] Add TLS encryption for telemetry
- [ ] Implement adaptive thresholds based on circadian patterns
- [ ] Extend to 10+ heterogeneous devices
- [ ] Add automated mitigation (device quarantine, rate limiting)

---

## Contributing

This is a research prototype. Contributions welcome for:
- Real hardware testing
- Additional attack vectors (ransomware, side-channel)
- Performance optimizations
- Integration with SIEM systems

---

---

**Based on:** Zachos, G., et al. (2022). "A Hybrid Intrusion Detection System for IoMT Networks." *IEEE Access*.

---

 <!--- ## Contact

**Your Name**  
📧 bhumireddisowmya@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/yourprofile) | [Portfolio](https://yourwebsite.com)

---
--- >

*Built as part of a Master's thesis project demonstrating practical cybersecurity skills for IoT/healthcare systems.*
