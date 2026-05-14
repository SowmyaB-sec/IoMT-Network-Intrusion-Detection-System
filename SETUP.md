# Testbed Setup Guide

This guide provides step-by-step instructions to replicate the IoMT IDS testbed using VirtualBox.

---

## System Requirements

### Host Machine
- **RAM**: 16GB minimum (8GB for host OS, 8GB for VMs)
- **Disk Space**: 50GB free
- **CPU**: Intel i5/i7 or AMD Ryzen equivalent
- **OS**: Windows 10+, macOS 10.15+, or Linux

### Software
- **VirtualBox**: 7.0+ ([Download](https://www.virtualbox.org/wiki/Downloads))
- **Ubuntu ISO**: 22.04 LTS Desktop 64-bit ([Download](https://ubuntu.com/download/desktop))

---

## Network Configuration

### 1. Create Host-Only Network

Open VirtualBox → **File** → **Host Network Manager** → **Create**

Configure **vboxnet0**:
```
IPv4 Address:  192.168.56.1
IPv4 Network Mask: 255.255.255.0
DHCP Server: Disabled
```
---

## VM Creation

### 2. Create Gateway VM

**VirtualBox Settings:**
- **Name**: IoMT-Gateway
- **Type**: Linux
- **Version**: Ubuntu (64-bit)
- **RAM**: 4096 MB
- **CPU**: 2 cores
- **Disk**: 20 GB (dynamically allocated)
- **Network Adapter 1**: Host-only Adapter (vboxnet0)

**Ubuntu Installation:**
1. Boot from Ubuntu 22.04 ISO
2. Choose **Minimal Installation**
3. Set hostname: `IoMT-Gateway`
4. Username: `iomt` (or your preference)
5. After installation, configure static IP:

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Paste:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 192.168.56.1/24
      dhcp4: no
```

Apply:
```bash
sudo netplan apply
ip addr show enp0s3  # Verify 192.168.56.1
```

### 3. Clone VMs for IoMT Devices

**Right-click IoMT-Gateway VM** → **Clone** → **Full Clone**

Create two clones:
- **IoMT-HeartMonitor** (192.168.56.101)
- **IoMT-GlucoseSensor** (192.168.56.102)

**For each cloned VM:**
1. Boot the VM
2. Change hostname:
```bash
sudo hostnamectl set-hostname IoMT-HeartMonitor  # or GlucoseSensor
```

3. Update static IP in `/etc/netplan/01-netcfg.yaml`:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 192.168.56.101/24  # Use .102 for GlucoseSensor
      dhcp4: no
      routes:
        - to: default
          via: 192.168.56.1
```

4. Apply and reboot:
```bash
sudo netplan apply
sudo reboot
```

---

## Software Installation

### 4. Install Dependencies on All VMs

Run on **all three VMs**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install python3-pip stress-ng hping3 net-tools -y

# Install Python libraries
pip3 install psutil pandas plotly
```

**Verify installations:**
```bash
python3 --version  # Should be 3.10+
pip3 list | grep psutil
stress-ng --version
hping3 --version
```

---

## Deploy Code

### 5. Copy Files to VMs

**On Gateway VM:**
```bash
cd ~
nano gateway_ids.py
# Paste code from repository
chmod +x gateway_ids.py
```

**On Device VMs (HeartMonitor, GlucoseSensor):**
```bash
cd ~
nano mda_agent.py
# Paste code from repository
chmod +x mda_agent.py
```

---

## Network Testing

### 6. Verify Connectivity

**From Gateway VM:**
```bash
ping -c 3 192.168.56.101  # HeartMonitor
ping -c 3 192.168.56.102  # GlucoseSensor
```

**From Device VMs:**
```bash
ping -c 3 192.168.56.1  # Gateway
```

All pings should succeed with 0% packet loss.

---

## Firewall Configuration

### 7. Open Detection Port on Gateway

```bash
# On Gateway VM only
sudo ufw allow 9999/tcp
sudo ufw enable
sudo ufw status  # Verify rule added
```

**Test port is listening:**
```bash
# On Gateway (after starting gateway_ids.py)
ss -tuln | grep 9999  # Should show LISTEN on 0.0.0.0:9999
```

---

## Running the System

### 8. Start Detection Engine

**On Gateway VM:**
```bash
python3 ~/gateway_ids.py
```

**Expected output:**
```
Gateway IDS listening on 192.168.56.1:9999 – waiting for IoMT devices...
```
A browser window will open showing the 4-panel dashboard (initially empty).

---

### 9. Start MDA Agents

**On HeartMonitor VM:**
```bash
nohup python3 ~/mda_agent.py > /dev/null 2>&1 &
```

**On GlucoseSensor VM:**
```bash
nohup python3 ~/mda_agent.py > /dev/null 2>&1 &
```

**Verify agents are running:**
```bash
ps aux | grep mda_agent
```

---

### 10. Verify Telemetry

**On Gateway terminal, you should see:**
```
Normal → IoMT-HeartMonitor | CPU 12.3% | MEM 45.2%
Normal → IoMT-GlucoseSensor | CPU 8.7% | MEM 38.9%
```
**Dashboard should populate** with two devices showing real-time graphs.

---

## Troubleshooting

### No telemetry received?
```bash
# Check firewall
sudo ufw status

# Check agent is sending
sudo tcpdump -i enp0s3 port 9999  # On gateway

# Restart agent
pkill -f mda_agent
nohup python3 ~/mda_agent.py > /dev/null 2>&1 &
```

### Dashboard not updating?
- Close all browser windows
- Restart `gateway_ids.py`
- Check for Python errors in terminal

### VM network issues?
```bash
# Reset netplan
sudo netplan apply
ip addr show enp0s3  # Verify IP address
```

---

## Next Steps

Once the baseline system is running (dashboard shows green metrics), proceed to [ATTACKS.md](ATTACKS.md) to simulate intrusion scenarios.
