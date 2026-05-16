# 🏠 Shadow Coordinator - IoT Exploitation
## CTF-SEK Advanced Challenge Writeup

[![Difficulty](https://img.shields.io/badge/Difficulty-Hard-red)](https://github.com/alrivera86/desafios-ctf-sek)
[![Category](https://img.shields.io/badge/Category-IoT%2FNetwork-darkgreen)](https://github.com/alrivera86/desafios-ctf-sek)
[![Files](https://img.shields.io/badge/Files-55-red)](https://github.com/alrivera86/desafios-ctf-sek)

---

## 📋 **Challenge Information**

- **Name**: Shadow Coordinator - IoT Network Infiltration
- **Category**: Internet of Things (IoT) + Network Security
- **Difficulty**: Hard
- **Files**: 55+ scripts, captures, analysis tools
- **Focus**: ZigBee networks, Smart home exploitation, Temperature monitoring bypass

---

## 🎯 **Challenge Description**

Desafío avanzado de IoT que simula la infiltración de una red doméstica inteligente controlada por un "Shadow Coordinator". Los participantes deben explotar dispositivos ZigBee, manipular sensores de temperatura, explotar smart locks, y finalmente comprometer el coordinador central que gestiona toda la red IoT.

---

## 📁 **Repository Structure**

```
shadow-coordinator-iot/
├── scripts/                    # 40+ Python exploitation scripts
├── iot-analysis/              # IoT protocol and device analysis
├── network-captures/          # PCAP files for network analysis
├── zigbee-data/              # ZigBee protocol specific data
├── documentation/            # Complete technical analysis
└── evidence/                 # Tokens, proofs, extracted data
```

---

## 🧰 **Technologies & Protocols**

### **IoT Stack**
- **ZigBee Protocol** - Mesh networking for smart devices
- **IEEE 802.15.4** - Physical layer protocol
- **Smart Lock Systems** - Physical access control
- **Temperature Sensors** - Environmental monitoring
- **WebSocket Communication** - Real-time device management

### **Attack Vectors**
- **ZigBee Network Infiltration** - Protocol-level attacks
- **Smart Device Buffer Overflow** - Memory corruption exploits
- **Temperature Anomaly Injection** - Sensor manipulation
- **Coordinator Takeover** - Network control hijacking
- **Firmware Static Analysis** - Device reverse engineering

---

## 🔍 **Key Scripts & Tools**

### **Core Exploitation Scripts (Selected)**
```python
# Network & Protocol Analysis
├── shadow_coordinator_exploit.py       # Main coordinator attack
├── system_coordinator_exploit.py       # Alternative system attack  
├── shadow_websocket.py                # WebSocket exploitation
├── websocket_exploit.py               # Real-time communication attack

# Device-Specific Attacks  
├── smart_lock_buffer_overflow.py      # Memory corruption exploit
├── smart_lock_exploit_clean.py        # Refined lock attack
├── temperature_anomaly_analysis.py    # Sensor manipulation
├── temperature_monitor.py             # Monitoring bypass

# Network Analysis
├── extended_websocket_monitor.py      # Traffic monitoring
├── websocket_snapshot_analysis.py     # Network state analysis
├── persistent_websocket.py            # Continuous monitoring
└── system_service_websocket_monitor.py # Service enumeration
```

### **Advanced Exploitation**
```python
# Token & Authentication
├── final_token_generation.py          # Authentication bypass
├── generate_strategic_tokens.py       # Token manipulation
├── test_tokens_manual.py             # Token validation testing

# Template & Injection Attacks
├── template_injection_exploit.py      # Server-side template injection
├── final_exploit_device_announcement.py # Device spoofing
├── ieee_flag_decode.py                # Protocol-level flag extraction

# Monitoring & Analysis
├── async_flag_monitor.py             # Asynchronous flag hunting
├── ultimate_flag_hunt.py             # Comprehensive flag search
└── final_flag_hunt.py                # Final extraction attempt
```

---

## 🌐 **Network Architecture**

### **ZigBee Mesh Network**
```
IoT Network Topology:
┌─────────────────────────────────────┐
│        Shadow Coordinator           │ ← Primary Target
│     (Network Controller)            │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┐
    │ ZigBee Hub │
    └─────┬─────┘
          │
   ┌──────┼──────┐
   │      │      │
┌──▼──┐ ┌─▼──┐ ┌─▼─────┐
│Smart│ │Temp│ │Motion │
│Lock │ │Sens│ │Detect │
└─────┘ └────┘ └───────┘
```

### **Attack Flow**
1. **Network Discovery** - ZigBee device enumeration
2. **Device Exploitation** - Smart lock/sensor compromise  
3. **Lateral Movement** - Network traversal
4. **Coordinator Access** - Central system takeover
5. **Flag Extraction** - Critical data exfiltration

---

## 📡 **ZigBee Protocol Analysis**

### **Network Captures Available**
```bash
network-captures/
├── capture_20260514_114936.pcap          # Initial discovery
├── capture_https_20260514_120136.pcap    # HTTPS traffic
├── git_diagnostics_capture.pcap          # Diagnostic data
├── git_parent_diagnostics_capture.pcap   # Parent coordinator
└── live_diagnostics.pcap                 # Real-time monitoring
```

### **ZigBee Data Files**
```bash
zigbee-data/
├── zigbee_network_20260514_115030.json      # Network topology
├── zigbee_network_auth_20260514_115116.json # Authentication data  
├── zigbee_topology_20260514_115125.json     # Device relationships
└── git_js_zigbee-console.js                 # Console interface
```

---

## 🔧 **IoT Analysis Tools**

### **FFUF Enumeration Results**
```bash
iot-analysis/
├── ffuf_iot_endpoints_20260514_114923.json        # IoT endpoint discovery
├── ffuf_shadow_coordinator_20260514_122454.json   # Coordinator enumeration (1.4MB)
├── git_js_app.js                                  # Main application (17KB)
├── git_js_settings.js                             # Configuration interface (28KB)
└── state_analysis.py                              # Network state analysis
```

---

## 🚀 **Exploitation Roadmap**

### **Phase 1: Network Discovery & Reconnaissance**
```bash
1. Analyze PCAP files for ZigBee network topology
2. Enumerate IoT devices using FFUF results  
3. Map device relationships and communication patterns
4. Identify coordinator IP and management interfaces
```

### **Phase 2: Device-Level Exploitation**  
```bash
1. Exploit smart lock buffer overflow vulnerability
2. Inject temperature anomalies to trigger alerts
3. Establish persistent access to sensor network
4. Collect authentication tokens and credentials
```

### **Phase 3: Coordinator Infiltration**
```bash
1. Use collected tokens for coordinator access
2. Exploit WebSocket communication channels
3. Perform template injection attacks
4. Achieve full network control
```

### **Phase 4: Flag Extraction**
```bash
1. Execute flag hunting scripts on coordinator
2. Decode IEEE protocol-level hidden data
3. Extract final flag from shadow coordinator system
4. Maintain persistence for additional objectives
```

---

## 🔒 **Security Implications**

### **IoT Vulnerabilities Demonstrated**
- **Weak Authentication** - Default/weak credentials on devices
- **Unencrypted Communication** - Plaintext IoT protocol data
- **Buffer Overflows** - Memory corruption in embedded devices  
- **Network Segmentation** - Lack of IoT network isolation
- **Firmware Security** - Vulnerable device firmware

### **Real-World Impact**
- **Home Automation Takeover** - Complete smart home control
- **Physical Security Bypass** - Smart lock exploitation
- **Privacy Invasion** - Sensor data manipulation
- **Network Lateral Movement** - IoT as attack vector
- **Persistence** - Long-term embedded access

---

## 📊 **Evidence & Results**

### **Extracted Tokens & Data**
```bash
evidence/
├── shadow_coordinator_tokens.txt     # Authentication tokens
├── generated_tokens.txt             # Generated access tokens  
├── operator_token.txt               # Operator-level access
├── target1_20260514_114839.html     # Target system interface
└── target2_20260514_114842.html     # Secondary target data
```

---

## 📚 **Learning Outcomes**

- **IoT Protocol Security** - ZigBee, IEEE 802.15.4 vulnerabilities
- **Embedded Device Exploitation** - Buffer overflows, firmware analysis
- **Network Analysis** - PCAP analysis, protocol decoding
- **Real-time Exploitation** - WebSocket attacks, persistent access
- **Smart Home Security** - Complete ecosystem compromise

---

## 🔗 **Resources & References**

### **IoT Security**
- [IoT Security Foundation](https://www.iotsecurityfoundation.org/)
- [ZigBee Security Research](https://research.checkpoint.com/2020/dont-be-silly-its-only-a-lightbulb/)
- [OWASP IoT Security](https://owasp.org/www-project-iot-security-verification-standard/)

### **Tools & Frameworks**
- **Wireshark** - Network protocol analysis
- **Killerbee** - ZigBee security testing framework  
- **Binwalk** - Firmware analysis
- **Scapy** - Custom packet crafting

---

## 💡 **Pro Tips**

1. **Start with Network Captures** - PCAP analysis reveals network topology
2. **Follow the JavaScript** - Web interfaces expose device management
3. **Token Correlation** - Multiple token files contain access credentials
4. **WebSocket Focus** - Real-time communication is key attack vector
5. **Temperature Anomalies** - Sensor manipulation triggers coordinator responses

---

## ⚡ **Quick Start Guide**

```bash
# 1. Analyze network topology
python3 scripts/websocket_snapshot_analysis.py

# 2. Extract coordinator info  
python3 scripts/shadow_coordinator_exploit.py

# 3. Device enumeration
python3 scripts/system_coordinator_exploit.py

# 4. Smart lock exploitation
python3 scripts/smart_lock_exploit_clean.py

# 5. Flag extraction
python3 scripts/ultimate_flag_hunt.py
```

---

## 📈 **Difficulty Progression**

| Phase | Difficulty | Skills Required |
|-------|------------|-----------------|
| Network Discovery | Medium | PCAP analysis, protocol knowledge |
| Device Exploitation | Hard | Binary exploitation, embedded systems |
| Coordinator Attack | Expert | Advanced web exploitation, real-time attacks |
| Flag Extraction | Expert | Custom tooling, protocol decoding |

---

*This challenge represents a comprehensive IoT security assessment requiring skills across multiple domains: network analysis, embedded systems, web exploitation, and protocol security.*

---

*Part of [desafios-ctf-sek](../) collection | Advanced IoT Security Challenge*