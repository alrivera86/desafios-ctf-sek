#!/usr/bin/env python3
"""
Temperature Anomaly Analysis for Shadow Coordinator
Los valores -3.8 y -4.1 son anómalos y podrían contener datos codificados
"""

import requests
import json
import struct
import binascii
from urllib3.exceptions import InsecureRequestWarning

requests.urllib3.disable_warnings(InsecureRequestWarning)

class TemperatureAnomalyExploit:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False

    def analyze_temperature_values(self):
        """Analyze anomalous temperature values for hidden data"""
        print("\n[*] Analyzing temperature anomalies...")

        # Anomalous values mentioned
        anomalous_temps = [-3.8, -4.1, -3.2, -4.5, -2.9]

        print(f"Anomalous temperatures: {anomalous_temps}")

        # Convert to different representations
        for temp in anomalous_temps:
            print(f"\nTemperature: {temp}")

            # Float32 representation
            float_bytes = struct.pack('f', temp)
            print(f"  Float32 bytes: {float_bytes.hex()}")
            print(f"  Float32 as int: {struct.unpack('I', float_bytes)[0]}")

            # ASCII interpretation
            try:
                ascii_chars = ''.join([chr(b) for b in float_bytes if 32 <= b <= 126])
                if ascii_chars:
                    print(f"  ASCII chars: {ascii_chars}")
            except:
                pass

            # Integer interpretation
            int_val = int(abs(temp * 10))  # Remove decimal, make positive
            print(f"  As integer: {int_val}")
            hex_val = hex(int_val)
            print(f"  As hex: {hex_val}")

            # Binary interpretation
            binary_val = bin(int_val)[2:]
            print(f"  As binary: {binary_val}")

    def test_temperature_as_coordinates(self):
        """Test if temperatures are coordinates or offsets"""
        print("\n[*] Testing temperatures as coordinates/offsets...")

        temps = [-3.8, -4.1]

        # Could be coordinates
        lat_lon_patterns = [
            (abs(temps[0]), abs(temps[1])),
            (temps[0] + 90, temps[1] + 180),  # Normalize to positive
            (int(temps[0] * 1000000), int(temps[1] * 1000000))  # Micro degrees
        ]

        for lat, lon in lat_lon_patterns:
            print(f"  Coordinates: {lat}, {lon}")

        # Could be array indices or memory offsets
        indices = [int(abs(t * 10)) for t in temps]
        print(f"  As indices: {indices}")

    def test_temperature_based_api_calls(self):
        """Use temperature values in API calls"""
        print("\n[*] Testing temperature values in API calls...")

        temps = [-3.8, -4.1, -3.2, -4.5, -2.9]

        # Try as entity IDs
        for temp in temps:
            entity_patterns = [
                f"sensor.temperature_{abs(temp)}",
                f"sensor.temp_{int(abs(temp * 10))}",
                f"binary_sensor.motion_{int(abs(temp))}",
                f"lock.door_{hex(int(abs(temp * 10)))[2:]}"
            ]

            for entity_id in entity_patterns:
                try:
                    response = self.session.get(f"{self.base_url}/api/v2/states/{entity_id}", timeout=5)
                    if response.status_code == 200:
                        print(f"[+] Found entity: {entity_id}")
                        print(f"    Response: {response.text[:200]}")
                except:
                    continue

    def test_temperature_as_unlock_codes(self):
        """Test temperatures as unlock codes or pin codes"""
        print("\n[*] Testing temperatures as unlock codes...")

        temps = [-3.8, -4.1, -3.2, -4.5, -2.9]

        # Convert to potential pin codes
        pin_codes = []
        for temp in temps:
            # Different conversion methods
            pin_variants = [
                str(int(abs(temp * 10))),  # 38, 41, etc
                str(int(abs(temp * 100))),  # 380, 410, etc
                hex(int(abs(temp * 10)))[2:],  # hex representation
                f"{int(abs(temp))}{int((abs(temp) % 1) * 10)}"  # split integer and decimal
            ]
            pin_codes.extend(pin_variants)

        print(f"Generated pin codes: {pin_codes}")

        # Test as unlock payloads
        headers = {'Content-Type': 'application/json'}

        for pin in pin_codes:
            unlock_payloads = [
                {
                    "cluster_id": 257,
                    "command": "unlock",
                    "pin_code": pin,
                    "nwk_address": "0x7B9C"
                },
                {
                    "entity_id": "lock.main_door",
                    "pin": pin
                },
                {
                    "service": "lock.unlock",
                    "pin_code": pin
                }
            ]

            for payload in unlock_payloads:
                try:
                    response = self.session.post(f"{self.base_url}/api/v2/services/lock/unlock",
                                               json=payload, headers=headers, timeout=5)
                    if response.status_code not in [401, 403, 404]:
                        print(f"  Interesting response for pin {pin}: {response.status_code}")
                        if 'flag{' in response.text or 'FLAG{' in response.text:
                            print(f"[!] FLAG FOUND with pin {pin}: {response.text}")
                            return response.text
                except:
                    continue

    def test_temperature_timing_patterns(self):
        """Test if temperature anomalies correspond to timing patterns"""
        print("\n[*] Testing temperature timing correlation...")

        # From PCAP analysis, we had these intervals
        pcap_intervals = [1.459, 1.043, 1.242, 1.735]
        temps = [-3.8, -4.1, -3.2, -4.5]

        # Look for mathematical relationships
        for i, temp in enumerate(temps):
            if i < len(pcap_intervals):
                interval = pcap_intervals[i]
                ratio = interval / abs(temp)
                print(f"  Temp {temp} / Interval {interval} = Ratio {ratio:.3f}")

                # Check if ratio reveals patterns
                if 0.3 < ratio < 0.5:  # Interesting ratio range
                    print(f"    [!] Interesting ratio: {ratio}")

    def decode_temperature_hex_patterns(self):
        """Decode temperatures as hex/binary data"""
        print("\n[*] Decoding temperatures as hex patterns...")

        temps = [-3.8, -4.1, -3.2, -4.5, -2.9]

        # Combine temperatures into hex string
        hex_parts = []
        for temp in temps:
            int_val = int(abs(temp * 10))
            hex_parts.append(f"{int_val:02x}")

        combined_hex = ''.join(hex_parts)
        print(f"Combined hex: {combined_hex}")

        try:
            decoded_bytes = bytes.fromhex(combined_hex)
            decoded_ascii = decoded_bytes.decode('ascii', errors='ignore')
            print(f"Decoded ASCII: '{decoded_ascii}'")

            # Look for flag patterns
            if 'flag' in decoded_ascii.lower() or any(c.isalpha() for c in decoded_ascii):
                print(f"[!] Potential flag data in temperatures: {decoded_ascii}")

        except:
            pass

        # Try different combinations
        for perm_length in [2, 3, 4]:
            import itertools
            for combo in itertools.combinations(temps, perm_length):
                hex_combo = ''.join([f"{int(abs(t * 10)):02x}" for t in combo])
                try:
                    decoded = bytes.fromhex(hex_combo).decode('ascii', errors='ignore')
                    if len(decoded.strip()) > 2:
                        print(f"  Combo {combo}: {hex_combo} -> '{decoded}'")
                except:
                    continue

    def test_temperature_steganography(self):
        """Check if temperatures hide steganographic data"""
        print("\n[*] Testing temperature steganography...")

        temps = [-3.8, -4.1, -3.2, -4.5, -2.9]

        # Extract decimal parts
        decimals = [abs(t) % 1 for t in temps]
        print(f"Decimal parts: {decimals}")

        # Extract fractional parts as binary
        binary_parts = []
        for decimal in decimals:
            # Convert to binary representation
            frac_int = int(decimal * 10)  # Get first decimal digit
            binary_parts.append(frac_int % 2)  # LSB

        binary_string = ''.join(map(str, binary_parts))
        print(f"Binary from decimals: {binary_string}")

        # Try to decode as ASCII
        if len(binary_string) >= 8:
            for i in range(0, len(binary_string) - 7, 8):
                byte = binary_string[i:i+8]
                if len(byte) == 8:
                    try:
                        char = chr(int(byte, 2))
                        if char.isprintable():
                            print(f"  Binary {byte} -> '{char}'")
                    except:
                        pass

    def run_all_temperature_analysis(self):
        """Run all temperature anomaly analysis"""
        print("="*60)
        print("Temperature Anomaly Analysis")
        print("="*60)

        analyses = [
            self.analyze_temperature_values,
            self.test_temperature_as_coordinates,
            self.test_temperature_based_api_calls,
            self.test_temperature_as_unlock_codes,
            self.test_temperature_timing_patterns,
            self.decode_temperature_hex_patterns,
            self.test_temperature_steganography
        ]

        for analysis in analyses:
            try:
                result = analysis()
                if result and ('flag{' in str(result) or 'FLAG{' in str(result)):
                    return result
            except Exception as e:
                print(f"[-] Analysis failed: {e}")
                continue

        return None

def main():
    base_url = "https://training.my-ctf.com:8812"

    exploit = TemperatureAnomalyExploit(base_url)
    result = exploit.run_all_temperature_analysis()

    if result:
        print(f"\n[!] FLAG FOUND: {result}")
    else:
        print("\n[-] No flag found in temperature analysis")

if __name__ == "__main__":
    main()