#!/usr/bin/env python3
"""
IEEE Address Decoding for Shadow Coordinator Flag
Target: 00:12:4B:00:24:AA:10:01
Try various decoding methods
"""
import base64
import binascii
import struct

def decode_ieee_address():
    """Decode the coordinator IEEE address in multiple ways"""
    ieee = "00:12:4B:00:24:AA:10:01"
    print(f"[*] Analyzing IEEE address: {ieee}")

    # Remove colons and get raw hex
    raw_hex = ieee.replace(':', '')
    print(f"[*] Raw hex: {raw_hex}")

    # Convert to bytes
    ieee_bytes = bytes.fromhex(raw_hex)
    print(f"[*] As bytes: {ieee_bytes}")
    print(f"[*] Byte values: {list(ieee_bytes)}")

    print("\n=== DECODING ATTEMPTS ===")

    # 1. Direct ASCII interpretation
    try:
        ascii_str = ieee_bytes.decode('ascii', errors='ignore')
        print(f"[1] ASCII: '{ascii_str}' (printable: {ascii_str.isprintable()})")
        if any(c.isalnum() for c in ascii_str):
            print(f"    [!] Potential text: {ascii_str}")
    except:
        print(f"[1] ASCII: Failed")

    # 2. Reverse byte order
    try:
        reversed_bytes = ieee_bytes[::-1]
        reversed_ascii = reversed_bytes.decode('ascii', errors='ignore')
        print(f"[2] Reversed ASCII: '{reversed_ascii}' (printable: {reversed_ascii.isprintable()})")
        if any(c.isalnum() for c in reversed_ascii):
            print(f"    [!] Potential reversed text: {reversed_ascii}")
    except:
        print(f"[2] Reversed ASCII: Failed")

    # 3. Base64 interpretation (if it were base64 encoded)
    try:
        # Try treating hex as base64
        base64_attempt = base64.b64decode(raw_hex + '==', validate=True)
        print(f"[3] Base64 decode: {base64_attempt}")
    except:
        print(f"[3] Base64: Not valid base64")

    # 4. XOR with common patterns
    print(f"\n[4] XOR attempts:")
    xor_keys = [0x00, 0xFF, 0x42, 0xAA, 0x55, 0x20]  # Common XOR keys
    for key in xor_keys:
        xored = bytes([b ^ key for b in ieee_bytes])
        xored_str = xored.decode('ascii', errors='ignore')
        if any(c.isalnum() for c in xored_str):
            print(f"    XOR {hex(key)}: '{xored_str}'")

    # 5. Interpret as structured data
    print(f"\n[5] Structured interpretations:")

    # Split into parts (common IEEE structure)
    oui = raw_hex[:6]  # Organizationally Unique Identifier
    extension = raw_hex[6:]
    print(f"    OUI: {oui} (hex: {oui})")
    print(f"    Extension: {extension}")

    # Look for patterns in each part
    try:
        oui_ascii = bytes.fromhex(oui).decode('ascii', errors='ignore')
        ext_ascii = bytes.fromhex(extension).decode('ascii', errors='ignore')
        print(f"    OUI as ASCII: '{oui_ascii}'")
        print(f"    Extension as ASCII: '{ext_ascii}'")
    except:
        pass

    # 6. Look for flag-like patterns
    print(f"\n[6] Flag pattern analysis:")

    # Convert each byte to chr and look for patterns
    char_analysis = []
    for i, byte in enumerate(ieee_bytes):
        char = chr(byte) if 32 <= byte <= 126 else f'\\x{byte:02x}'
        char_analysis.append(f"pos{i}: {byte:02x} -> '{char}'")

    print("    Byte-by-byte character analysis:")
    for analysis in char_analysis:
        print(f"      {analysis}")

    # 7. Binary analysis
    print(f"\n[7] Binary representation:")
    binary_str = ''.join(format(byte, '08b') for byte in ieee_bytes)
    print(f"    Binary: {binary_str}")

    # Look for patterns in binary
    if '1111' in binary_str or '0000' in binary_str:
        print(f"    [!] Contains repeated patterns")

    # 8. Mathematical operations
    print(f"\n[8] Mathematical interpretations:")

    # Treat as big-endian integer
    big_int = int.from_bytes(ieee_bytes, 'big')
    little_int = int.from_bytes(ieee_bytes, 'little')

    print(f"    Big-endian int: {big_int}")
    print(f"    Little-endian int: {little_int}")
    print(f"    Big-endian hex: 0x{big_int:x}")
    print(f"    Little-endian hex: 0x{little_int:x}")

    # 9. Look for embedded coordinates or other data
    print(f"\n[9] Special interpretations:")

    # Split into 4-byte chunks
    if len(ieee_bytes) == 8:
        chunk1 = ieee_bytes[:4]
        chunk2 = ieee_bytes[4:]

        # Try as floats
        try:
            float1 = struct.unpack('!f', chunk1)[0]  # Big-endian float
            float2 = struct.unpack('!f', chunk2)[0]
            print(f"    As big-endian floats: {float1}, {float2}")
        except:
            pass

        try:
            float1 = struct.unpack('<f', chunk1)[0]  # Little-endian float
            float2 = struct.unpack('<f', chunk2)[0]
            print(f"    As little-endian floats: {float1}, {float2}")
        except:
            pass

    # 10. CTF-specific patterns
    print(f"\n[10] CTF-specific analysis:")

    # Common CTF transformations
    hex_as_ascii = ''.join(chr(int(raw_hex[i:i+2], 16)) for i in range(0, len(raw_hex), 2) if 32 <= int(raw_hex[i:i+2], 16) <= 126)
    if hex_as_ascii:
        print(f"    Hex-to-ASCII: '{hex_as_ascii}'")
        if 'flag' in hex_as_ascii.lower() or len(hex_as_ascii) > 3:
            print(f"    [!] Potential flag text: {hex_as_ascii}")

    # ROT13 on any text found
    import codecs
    if hex_as_ascii:
        rot13 = codecs.encode(hex_as_ascii, 'rot13')
        print(f"    ROT13: '{rot13}'")

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"IEEE Address: {ieee}")
    print(f"Most likely interpretations:")

    candidates = []

    if hex_as_ascii and len(hex_as_ascii) > 2:
        candidates.append(f"Direct hex-to-ASCII: '{hex_as_ascii}'")

    if ascii_str.isprintable() and len(ascii_str.strip()) > 1:
        candidates.append(f"Raw bytes as ASCII: '{ascii_str}'")

    if reversed_ascii.isprintable() and len(reversed_ascii.strip()) > 1:
        candidates.append(f"Reversed bytes as ASCII: '{reversed_ascii}'")

    if candidates:
        for candidate in candidates:
            print(f"  - {candidate}")
    else:
        print("  - No obvious flag encoding found in IEEE address")

    return candidates

if __name__ == "__main__":
    print("=== SHADOW COORDINATOR IEEE FLAG ANALYSIS ===")
    candidates = decode_ieee_address()

    if any('flag' in c.lower() for c in candidates):
        print("\n[!!!] POTENTIAL FLAG FOUND IN IEEE ADDRESS!")
        for candidate in candidates:
            if 'flag' in candidate.lower():
                print(f"FLAG: {candidate}")
    else:
        print("\n[INFO] No obvious flag in IEEE address")