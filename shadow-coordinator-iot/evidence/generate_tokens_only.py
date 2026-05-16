#!/usr/bin/env python3
"""
Generate Strategic Tokens (Offline Version)
Frame 307 Analysis and Token Generation without API testing
"""

import hashlib
import base64
import binascii
import struct
import time
import hmac

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

def generate_all_tokens():
    """Generate all strategic token candidates and save to file"""
    candidates = []

    print("=== Frame 307 Based Tokens ===")
    # MD5 of frame data
    frame_md5 = hashlib.md5(FRAME_307_BYTES).hexdigest()
    candidates.append(("frame_md5", frame_md5))
    print(f"frame_md5: {frame_md5}")

    # SHA256 of frame data
    frame_sha256 = hashlib.sha256(FRAME_307_BYTES).hexdigest()
    candidates.append(("frame_sha256", frame_sha256))
    print(f"frame_sha256: {frame_sha256}")

    # Base64 of frame data
    frame_b64 = base64.b64encode(FRAME_307_BYTES).decode()
    candidates.append(("frame_b64", frame_b64))
    print(f"frame_b64: {frame_b64}")

    # First 16 bytes of frame as hex
    frame_16 = FRAME_307_HEX[:32]
    candidates.append(("frame_16_hex", frame_16))
    print(f"frame_16_hex: {frame_16}")

    # Last 16 bytes of frame as hex
    frame_last16 = FRAME_307_HEX[-32:]
    candidates.append(("frame_last16_hex", frame_last16))
    print(f"frame_last16_hex: {frame_last16}")

    print("\n=== Device-Specific Tokens ===")
    # IEEE address transformations
    ieee_clean = IEEE_ADDRESS_HEX
    candidates.append(("ieee_hex", ieee_clean))
    print(f"ieee_hex: {ieee_clean}")

    ieee_md5 = hashlib.md5(ieee_clean.encode()).hexdigest()
    candidates.append(("ieee_md5", ieee_md5))
    print(f"ieee_md5: {ieee_md5}")

    ieee_sha256 = hashlib.sha256(ieee_clean.encode()).hexdigest()
    candidates.append(("ieee_sha256", ieee_sha256))
    print(f"ieee_sha256: {ieee_sha256}")

    # NWK address (0x7B9C) transformations
    nwk_hex = hex(DEVICE_NWK_INT)[2:]
    candidates.append(("nwk_hex", nwk_hex))
    print(f"nwk_hex: {nwk_hex}")

    nwk_padded = f"{DEVICE_NWK_INT:08x}"
    candidates.append(("nwk_padded", nwk_padded))
    print(f"nwk_padded: {nwk_padded}")

    nwk_reversed = nwk_hex[::-1]
    candidates.append(("nwk_reversed", nwk_reversed))
    print(f"nwk_reversed: {nwk_reversed}")

    # Capability + Sequence combinations
    cap_seq = f"{CAPABILITY:02x}{SEQUENCE:02x}"
    candidates.append(("cap_seq", cap_seq))
    print(f"cap_seq: {cap_seq}")

    cap_seq_md5 = hashlib.md5(cap_seq.encode()).hexdigest()
    candidates.append(("cap_seq_md5", cap_seq_md5))
    print(f"cap_seq_md5: {cap_seq_md5}")

    # Cluster ID variations
    cluster_hex = f"{CLUSTER:04x}"
    candidates.append(("cluster_hex", cluster_hex))
    print(f"cluster_hex: {cluster_hex}")

    cluster_padded = f"{CLUSTER:08x}"
    candidates.append(("cluster_padded", cluster_padded))
    print(f"cluster_padded: {cluster_padded}")

    print("\n=== Mathematical Pattern Tokens ===")
    # Temperature ratio applied
    ratio_int = int(TEMPERATURE_RATIO * 1000000)  # 380000
    ratio_hex = f"{ratio_int:x}"
    candidates.append(("temp_ratio_int", ratio_hex))
    print(f"temp_ratio_int: {ratio_hex}")

    ratio_md5 = hashlib.md5(str(ratio_int).encode()).hexdigest()
    candidates.append(("temp_ratio_md5", ratio_md5))
    print(f"temp_ratio_md5: {ratio_md5}")

    # Sequence 51 variations
    seq_variations = [
        f"{SEQUENCE:02x}",
        f"{SEQUENCE:08x}",
        f"{SEQUENCE ** 2:x}",
        f"{SEQUENCE * CAPABILITY:x}"
    ]
    for i, var in enumerate(seq_variations):
        candidates.append((f"seq_var_{i}", var))
        print(f"seq_var_{i}: {var}")

    print("\n=== Timestamp-Based Tokens ===")
    timestamp_int = int(TIMESTAMP)
    timestamp_ms = int(TIMESTAMP * 1000)

    timestamp_hex = f"{timestamp_int:x}"
    candidates.append(("timestamp_int", timestamp_hex))
    print(f"timestamp_int: {timestamp_hex}")

    timestamp_ms_hex = f"{timestamp_ms:x}"
    candidates.append(("timestamp_ms", timestamp_ms_hex))
    print(f"timestamp_ms: {timestamp_ms_hex}")

    timestamp_md5 = hashlib.md5(str(timestamp_int).encode()).hexdigest()
    candidates.append(("timestamp_md5", timestamp_md5))
    print(f"timestamp_md5: {timestamp_md5}")

    print("\n=== Combined Tokens ===")
    # IEEE + NWK
    ieee_nwk = ieee_clean + nwk_hex
    candidates.append(("ieee_nwk", ieee_nwk))
    print(f"ieee_nwk: {ieee_nwk}")

    ieee_nwk_md5 = hashlib.md5(ieee_nwk.encode()).hexdigest()
    candidates.append(("ieee_nwk_md5", ieee_nwk_md5))
    print(f"ieee_nwk_md5: {ieee_nwk_md5}")

    # All device identifiers
    device_combo = f"{ieee_clean}{nwk_hex}{cap_seq}{cluster_hex}"
    candidates.append(("device_combo", device_combo))
    print(f"device_combo: {device_combo}")

    device_combo_md5 = hashlib.md5(device_combo.encode()).hexdigest()
    candidates.append(("device_combo_md5", device_combo_md5))
    print(f"device_combo_md5: {device_combo_md5}")

    device_combo_sha256 = hashlib.sha256(device_combo.encode()).hexdigest()
    candidates.append(("device_combo_sha256", device_combo_sha256))
    print(f"device_combo_sha256: {device_combo_sha256}")

    print("\n=== Frame Structure Tokens ===")
    # Source address from frame: 0x55aa
    src_addr = "55aa"
    candidates.append(("src_addr", src_addr))
    print(f"src_addr: {src_addr}")

    src_addr_md5 = hashlib.md5(src_addr.encode()).hexdigest()
    candidates.append(("src_addr_md5", src_addr_md5))
    print(f"src_addr_md5: {src_addr_md5}")

    # PAN ID: 0x1234
    pan_id = "1234"
    candidates.append(("pan_id", pan_id))
    print(f"pan_id: {pan_id}")

    pan_id_md5 = hashlib.md5(pan_id.encode()).hexdigest()
    candidates.append(("pan_id_md5", pan_id_md5))
    print(f"pan_id_md5: {pan_id_md5}")

    # Combined frame identifiers
    frame_combo = f"{src_addr}{pan_id}{nwk_hex}"
    candidates.append(("frame_combo", frame_combo))
    print(f"frame_combo: {frame_combo}")

    frame_combo_md5 = hashlib.md5(frame_combo.encode()).hexdigest()
    candidates.append(("frame_combo_md5", frame_combo_md5))
    print(f"frame_combo_md5: {frame_combo_md5}")

    print("\n=== HMAC Tokens ===")
    # HMAC variations (using known data as key)
    hmac_key = FRAME_307_BYTES[:16]  # First 16 bytes as key
    hmac_data = ieee_clean.encode()
    hmac_result = hmac.new(hmac_key, hmac_data, hashlib.sha256).hexdigest()
    candidates.append(("hmac_frame_ieee", hmac_result))
    print(f"hmac_frame_ieee: {hmac_result}")

    print("\n=== CTF-Specific Tokens ===")
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
        print(f"ctf_{pattern}: {pattern}")

        pattern_md5 = hashlib.md5(pattern.encode()).hexdigest()
        candidates.append((f"ctf_{pattern}_md5", pattern_md5))
        print(f"ctf_{pattern}_md5: {pattern_md5}")

    print("\n=== Additional Strategic Tokens ===")
    # XOR patterns
    ieee_bytes = bytes.fromhex(IEEE_ADDRESS_HEX)
    nwk_bytes = struct.pack('>H', DEVICE_NWK_INT)

    # XOR IEEE with NWK repeated
    xor_result = bytes(a ^ b for a, b in zip(ieee_bytes, (nwk_bytes * 4)[:len(ieee_bytes)]))
    xor_hex = xor_result.hex()
    candidates.append(("xor_ieee_nwk", xor_hex))
    print(f"xor_ieee_nwk: {xor_hex}")

    # Frame data XOR with device identifiers
    device_bytes = ieee_bytes + nwk_bytes
    frame_xor = bytes(a ^ b for a, b in zip(FRAME_307_BYTES[:len(device_bytes)], device_bytes))
    frame_xor_hex = frame_xor.hex()
    candidates.append(("frame_xor_device", frame_xor_hex))
    print(f"frame_xor_device: {frame_xor_hex}")

    # Key bytes analysis from Frame 307
    print(f"\n=== Frame 307 Key Byte Analysis ===")
    print(f"Full frame: {FRAME_307_HEX}")
    print(f"Frame length: {len(FRAME_307_BYTES)} bytes")

    # Extract potential key segments
    segments = []
    for i in range(0, len(FRAME_307_BYTES), 4):
        segment = FRAME_307_BYTES[i:i+4]
        if len(segment) == 4:
            seg_hex = segment.hex()
            segments.append(seg_hex)
            candidates.append((f"frame_seg_{i//4}", seg_hex))
            print(f"frame_seg_{i//4}: {seg_hex}")

    # Save to file
    with open('/home/pheaker/Documents/CTF/generated_tokens.txt', 'w') as f:
        f.write("=== Shadow Coordinator Strategic Tokens ===\n")
        f.write(f"Generated from Frame 307: {FRAME_307_HEX}\n")
        f.write(f"Device NWK: {DEVICE_NWK}\n")
        f.write(f"IEEE Address: {IEEE_ADDRESS}\n")
        f.write(f"Capability: 0x{CAPABILITY:02x}\n")
        f.write(f"Sequence: {SEQUENCE}\n")
        f.write(f"Cluster: 0x{CLUSTER:04x}\n\n")

        for desc, token in candidates:
            f.write(f"{desc}: {token}\n")

    print(f"\n✅ Generated {len(candidates)} token candidates")
    print("✅ Saved to: /home/pheaker/Documents/CTF/generated_tokens.txt")

    return candidates

if __name__ == "__main__":
    generate_all_tokens()