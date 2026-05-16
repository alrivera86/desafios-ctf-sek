#!/usr/bin/env python3
"""
Generate precise authentication token based on all Shadow Coordinator findings
"""

import hashlib
import base64

def generate_shadow_coordinator_token():
    """Generate token based on exact PCAP frame 307 analysis"""

    # Frame 307 exact data from PCAP analysis
    frame_data = {
        'number': 307,
        'size': 39,
        'nwk': '0x7B9C',
        'ieee': '00:15:8d:00:02:1a:2b:3c',
        'sequence': 51,
        'capability': 0x8e,
        'cluster': 0x0013,  # Device announcement cluster
        'pan_id': 0x1234
    }

    # Temperature anomalies converted to hex
    temp_hex = ['26', '29', '20', '2d', '1d']  # From temperature analysis

    # Timing intervals from PCAP
    timing_intervals = [1459, 1043, 1242, 1735]  # milliseconds

    print("Generating Shadow Coordinator tokens...")

    potential_tokens = []

    # Method 1: Frame-based tokens
    frame_tokens = [
        f"frame_{frame_data['number']}_{frame_data['size']}",
        f"device_{frame_data['nwk'][2:]}",  # Remove 0x prefix
        f"announce_{frame_data['sequence']}",
        f"{frame_data['ieee'].replace(':', '')}_{frame_data['number']}",
        f"capability_{frame_data['capability']:02x}",
        f"pan_{frame_data['pan_id']:04x}_nwk_{frame_data['nwk'][2:]}",
    ]

    potential_tokens.extend(frame_tokens)

    # Method 2: Temperature correlation tokens
    temp_tokens = [
        ''.join(temp_hex),  # "2629202d1d"
        ''.join(temp_hex[:2]),  # "2629"
        f"temp_{''.join(temp_hex[:3])}",  # "temp_262920"
        str(int(''.join(temp_hex[:2]), 16)),  # Decimal of "2629"
    ]

    potential_tokens.extend(temp_tokens)

    # Method 3: Combined frame + temperature
    combined_tokens = [
        f"{frame_data['nwk'][2:]}_{''.join(temp_hex[:2])}",  # "7B9C_2629"
        f"unlock_{frame_data['number']}_{temp_hex[0]}",  # "unlock_307_26"
        f"device_announce_{frame_data['sequence']}_{temp_hex[1]}",  # "device_announce_51_29"
    ]

    potential_tokens.extend(combined_tokens)

    # Method 4: Timing-based tokens
    timing_tokens = [
        str(timing_intervals[0]),  # "1459"
        f"timing_{timing_intervals[0]}_{timing_intervals[1]}",
        f"interval_{int(sum(timing_intervals[:2])/2)}",  # Average interval
    ]

    potential_tokens.extend(timing_tokens)

    # Method 5: Shadow Coordinator specific
    coordinator_tokens = [
        "shadow_coordinator",
        "coordinator_unlock",
        "coordinator_shadow",
        "unlock_shadow",
        f"coordinator_{frame_data['nwk'][2:]}",
        f"shadow_{frame_data['ieee'].replace(':', '')[:8]}",
    ]

    potential_tokens.extend(coordinator_tokens)

    # Method 6: Hash-based tokens (commonly used in CTFs)
    hash_base = f"{frame_data['nwk']}_{frame_data['ieee']}_{frame_data['number']}"
    hash_tokens = [
        hashlib.md5(hash_base.encode()).hexdigest(),
        hashlib.sha1(hash_base.encode()).hexdigest()[:32],
        hashlib.sha256(hash_base.encode()).hexdigest()[:32],
        base64.b64encode(hash_base.encode()).decode().rstrip('='),
    ]

    potential_tokens.extend(hash_tokens)

    # Method 7: Specific patterns that might work
    pattern_tokens = [
        f"token_{frame_data['nwk'][2:].lower()}",
        f"auth_{frame_data['sequence']:02d}",
        f"device_{frame_data['capability']:02x}_{frame_data['number']}",
        f"zigbee_{temp_hex[0]}{temp_hex[1]}",
        f"unlock_code_{timing_intervals[0]}",
    ]

    potential_tokens.extend(pattern_tokens)

    print(f"Generated {len(potential_tokens)} potential tokens")

    return potential_tokens

def test_token_formats():
    """Test different token format variations"""
    base_tokens = generate_shadow_coordinator_token()

    all_tokens = []

    # Add base tokens
    all_tokens.extend(base_tokens)

    # Add uppercase variations
    all_tokens.extend([token.upper() for token in base_tokens[:10]])

    # Add JWT-like format (just base64 encoding)
    for token in base_tokens[:5]:
        jwt_like = f"eyJhbGciOiJIUzI1NiJ9.{base64.b64encode(token.encode()).decode().rstrip('=')}.signature"
        all_tokens.append(jwt_like)

    # Add Bearer format
    for token in base_tokens[:5]:
        all_tokens.append(f"Bearer {token}")

    return all_tokens

if __name__ == "__main__":
    tokens = test_token_formats()

    print("\nTop 20 most likely tokens:")
    for i, token in enumerate(tokens[:20]):
        print(f"{i+1:2d}. {token}")

    print(f"\nTotal tokens generated: {len(tokens)}")

    # Save to file for testing
    with open('/home/pheaker/Documents/CTF/shadow_coordinator_tokens.txt', 'w') as f:
        for token in tokens:
            f.write(f"{token}\n")

    print("Tokens saved to shadow_coordinator_tokens.txt")