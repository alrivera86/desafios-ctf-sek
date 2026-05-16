#!/usr/bin/env python3
import requests
import time
import json

# Get token
resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                    json={"username":"admin","password":"admin1234"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("[*] === MONITORING SHADOW COORDINATOR TEMPERATURE CHANGES ===")
print("[*] Hypothesis: Temperature values are encoding flag data")

collected_values = []
previous_temp = None

for i in range(60):  # Monitor for 60 iterations
    try:
        resp = requests.get("https://training.my-ctf.com:8812/api/v2/states",
                          headers=headers, verify=False)
        data = resp.json()
        entities = data.get('entities', [])

        # Get temperature sensor
        temp_sensor = next((e for e in entities if e.get('entity_id') == 'sensor.north_hall_temperature'), None)
        if temp_sensor:
            current_temp = temp_sensor.get('state')
            timestamp = time.strftime("%H:%M:%S")

            if current_temp != previous_temp:
                print(f"[{timestamp}] Temperature changed: {previous_temp} -> {current_temp}")

                if current_temp not in collected_values:
                    collected_values.append(current_temp)

                # Try to interpret the value
                if isinstance(current_temp, (int, float)):
                    abs_val = int(abs(current_temp))

                    # ASCII interpretation
                    if 32 <= abs_val <= 126:
                        ascii_char = chr(abs_val)
                        print(f"    ASCII interpretation: {ascii_char}")

                    # Hex interpretation
                    hex_val = hex(abs_val)
                    print(f"    Hex: {hex_val}")

                    # Binary
                    bin_val = bin(abs_val)
                    print(f"    Binary: {bin_val}")

                previous_temp = current_temp

        # Also check the coordinator status
        coordinator = next((e for e in entities if e.get('entity_id') == 'sensor.zb_gw_03_status'), None)
        if coordinator and coordinator.get('state') != 'unlocked':
            print(f"[{timestamp}] Coordinator state changed: {coordinator.get('state')}")

        time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)

print(f"\\n=== ANALYSIS OF COLLECTED VALUES ===")
print(f"Collected temperature values: {collected_values}")

# Try to decode collected values as ASCII
if collected_values:
    print("\\n=== ASCII DECODE ATTEMPTS ===")

    # Try absolute values as ASCII
    ascii_chars = []
    for val in collected_values:
        if isinstance(val, (int, float)):
            abs_val = int(abs(val))
            if 32 <= abs_val <= 126:
                ascii_chars.append(chr(abs_val))
            else:
                ascii_chars.append('?')

    ascii_string = ''.join(ascii_chars)
    print(f"ASCII string: {ascii_string}")

    # Try different interpretations
    print("\\n=== ALTERNATIVE INTERPRETATIONS ===")

    # As decimal values
    decimal_string = ''.join(str(int(abs(v))) for v in collected_values if isinstance(v, (int, float)))
    print(f"Decimal concatenated: {decimal_string}")

    # As hex values
    hex_values = [hex(int(abs(v))) for v in collected_values if isinstance(v, (int, float))]
    print(f"Hex values: {hex_values}")

    # Check if decimal string contains flag pattern
    if 'flag' in decimal_string.lower() or 'ctf' in decimal_string.lower():
        print(f"[!] POTENTIAL FLAG IN DECIMAL: {decimal_string}")

    if 'flag' in ascii_string.lower() or 'ctf' in ascii_string.lower():
        print(f"[!] POTENTIAL FLAG IN ASCII: {ascii_string}")

print("\\n[*] Temperature monitoring complete.")