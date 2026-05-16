#!/usr/bin/env python3
import requests
import json

# Get token
resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                    json={"username":"admin","password":"admin1234"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("[*] === COMPREHENSIVE STATE ANALYSIS ===")

# Check both targets for unusual states
targets = [
    ("HTTP", "http://training-pod2.ctfchile.com:32780"),
    ("HTTPS", "https://training.my-ctf.com:8812")
]

all_states = {}

for target_name, target_url in targets:
    print(f"\n=== {target_name} TARGET ANALYSIS ===")

    try:
        # Get states
        resp = requests.get(f"{target_url}/api/v2/states", headers=headers, verify=False)
        data = resp.json()
        entities = data.get('entities', [])

        print(f"Found {len(entities)} entities")

        for entity in entities:
            entity_id = entity.get('entity_id', '')
            state = entity.get('state', '')

            all_states[f"{target_name}_{entity_id}"] = state

            # Look for unusual states
            unusual_patterns = []

            if entity.get('user_override'):
                unusual_patterns.append(f"USER_OVERRIDE by {entity.get('overridden_by', 'unknown')}")

            if str(state).lower() in ['unlocked', 'locked', 'flag', 'ctf']:
                unusual_patterns.append(f"SUSPICIOUS_STATE: {state}")

            if isinstance(state, (int, float)) and (state < -10 or state > 100):
                unusual_patterns.append(f"UNUSUAL_NUMERIC: {state}")

            if isinstance(state, str) and len(state) > 20:
                unusual_patterns.append(f"LONG_STRING: {state[:50]}...")

            # Check for base64-like strings
            if isinstance(state, str) and len(state) > 8 and state.replace('=', '').replace('+', '').replace('/', '').isalnum():
                try:
                    import base64
                    decoded = base64.b64decode(state + '==').decode('utf-8', errors='ignore')
                    if any(word in decoded.lower() for word in ['flag', 'ctf', 'shadow']):
                        unusual_patterns.append(f"BASE64_FLAG: {decoded}")
                except:
                    pass

            if unusual_patterns:
                print(f"\n[!] UNUSUAL: {entity_id}")
                print(f"    Entity: {entity.get('name', 'N/A')}")
                print(f"    State: {state}")
                print(f"    Patterns: {', '.join(unusual_patterns)}")
                if entity.get('nwk'):
                    print(f"    Network: {entity.get('nwk')} / {entity.get('ieee', 'N/A')}")

        # Get topology for additional info
        topo_resp = requests.get(f"{target_url}/api/v2/zigbee/topology", headers=headers, verify=False)
        if topo_resp.status_code == 200:
            topo_data = topo_resp.json()
            print(f"\n=== {target_name} TOPOLOGY STATES ===")
            for node in topo_data.get('nodes', []):
                node_state = node.get('state', '')
                if str(node_state) not in ['online', 'home', 'on', 'off'] and node_state != '':
                    print(f"[!] UNUSUAL TOPOLOGY STATE: {node.get('name', 'N/A')} -> {node_state}")

                    # Check if this could be encoded data
                    if isinstance(node_state, str) and len(str(node_state)) > 5:
                        print(f"    Analyzing: {node_state}")

                        # Try different encodings
                        try:
                            # Hex decode
                            if all(c in '0123456789abcdefABCDEF' for c in str(node_state)):
                                hex_decoded = bytes.fromhex(str(node_state)).decode('utf-8', errors='ignore')
                                if 'flag' in hex_decoded.lower() or 'ctf' in hex_decoded.lower():
                                    print(f"    [!] HEX_DECODED: {hex_decoded}")
                        except:
                            pass

                        # ASCII conversion
                        if isinstance(node_state, (int, float)):
                            try:
                                ascii_char = chr(int(node_state)) if 32 <= int(node_state) <= 126 else None
                                if ascii_char:
                                    print(f"    ASCII: {ascii_char}")
                            except:
                                pass

    except Exception as e:
        print(f"Error analyzing {target_name}: {e}")

print(f"\n=== CROSS-TARGET COMPARISON ===")
# Compare states between targets
for key in all_states:
    if key.startswith('HTTP_'):
        https_key = key.replace('HTTP_', 'HTTPS_')
        if https_key in all_states:
            http_state = all_states[key]
            https_state = all_states[https_key]
            if http_state != https_state:
                entity_name = key.replace('HTTP_', '')
                print(f"[!] DIFFERENCE in {entity_name}:")
                print(f"    HTTP:  {http_state}")
                print(f"    HTTPS: {https_state}")

print("\n[*] State analysis complete.")