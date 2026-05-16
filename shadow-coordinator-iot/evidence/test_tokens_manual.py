#!/usr/bin/env python3
"""
Manual Token Tester for Shadow Coordinator CTF
Test generated tokens against the unlock API
"""

import requests
import json
import time

# Configuration
API_URL = "http://training-pod2.ctfchile.com:32785/api/v2/services/lock/unlock"
OPERATOR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcGVyYXRvciIsInJvbGUiOiJ1c2VyIiwibmFtZSI6IkZhY2lsaXRpZXMgT3BlcmF0b3IiLCJpYXQiOjE3Nzg3NzQ0MjAsImV4cCI6MTc3ODgwMzIyMH0.W0p3F7i98Dxlwar9A1NPR85sLGHd72GuRa88rRtJT34"

# Load generated tokens
def load_tokens():
    tokens = []
    try:
        with open('/home/pheaker/Documents/CTF/generated_tokens.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line and not line.startswith('=') and not line.startswith('Generated') and not line.startswith('Device'):
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        desc, token = parts
                        tokens.append((desc, token))
    except Exception as e:
        print(f"Error loading tokens: {e}")
    return tokens

def test_single_token(token, description="", verbose=True):
    """Test a single token against the API"""
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

        if verbose:
            print(f"[{response.status_code}] {description}: {token[:50]}{'...' if len(token) > 50 else ''}")

        if response.status_code == 200:
            try:
                result = response.json()
                if verbose:
                    print(f"    ✅ SUCCESS! Response: {result}")
                if 'flag' in str(result).lower():
                    print(f"🎉 FLAG FOUND! Token: {token}")
                    print(f"🚩 Response: {result}")
                    return True, result
                return True, result
            except:
                if verbose:
                    print(f"    ✅ SUCCESS! Response text: {response.text}")
                if 'flag' in response.text.lower():
                    print(f"🎉 FLAG FOUND! Token: {token}")
                    print(f"🚩 Response: {response.text}")
                    return True, response.text
                return True, response.text

        elif response.status_code == 401:
            if verbose:
                print(f"    ❌ Unauthorized")
        elif response.status_code == 403:
            if verbose:
                print(f"    ❌ Forbidden")
        elif response.status_code == 404:
            if verbose:
                print(f"    ❌ Not Found")
        else:
            if verbose:
                print(f"    ⚠️  Unexpected response: {response.text}")

        return False, response.text if hasattr(response, 'text') else None

    except requests.exceptions.ConnectTimeout:
        if verbose:
            print(f"    ❌ Connection timeout")
        return False, "timeout"
    except requests.exceptions.ConnectionError as e:
        if verbose:
            print(f"    ❌ Connection error: {e}")
        return False, "connection_error"
    except Exception as e:
        if verbose:
            print(f"    ❌ Error: {e}")
        return False, str(e)

def test_all_tokens():
    """Test all generated tokens"""
    tokens = load_tokens()

    print(f"=== Testing {len(tokens)} Generated Tokens ===")
    print(f"Target: {API_URL}")
    print("=" * 60)

    successful_tokens = []

    for i, (desc, token) in enumerate(tokens, 1):
        print(f"\n[{i:2d}/{len(tokens)}]", end=" ")
        success, result = test_single_token(token, desc)

        if success:
            successful_tokens.append((desc, token, result))
            # If we find a flag, we can stop
            if 'flag' in str(result).lower():
                break

        # Small delay to avoid rate limiting
        time.sleep(0.2)

    print("\n" + "=" * 60)

    if successful_tokens:
        print(f"✅ Found {len(successful_tokens)} successful tokens:")
        for desc, token, result in successful_tokens:
            print(f"  - {desc}: {token}")
            if 'flag' in str(result).lower():
                print(f"    🚩 FLAG RESULT: {result}")
    else:
        print("❌ No successful tokens found")

    return successful_tokens

def test_specific_tokens():
    """Test specific high-priority tokens manually"""
    print("=== Testing High-Priority Tokens ===")

    # High priority candidates based on CTF patterns
    high_priority = [
        ("frame_md5", "396c7daa68b865aa506fd4ae9559034d"),
        ("frame_sha256", "c48544f7870fa47fe38d8fdb38741bd63584fbefe21165ec943df5869eb30683"),
        ("ieee_md5", "57c55346a26d1ecaa598ab523a895c03"),
        ("device_combo_md5", "2bc82c3e9befb55464e67d9107f4152c"),
        ("device_combo_sha256", "b200c05a867c8d27b58ecc5d0b60b9cee918a7cec55c4c033ee264e46251a145"),
        ("hmac_frame_ieee", "042b98e29775c78aad7d2e2124e534671485f461ddff9547805fdee7f82bf751"),
        ("ctf_shadow7b9c_md5", "67670e139e17b58528210c2ae741f9ba"),
        ("ctf_coordinator51_md5", "dbe43db828176e5feaa64ce66790d4ec"),
        ("ctf_lock8e33_md5", "6b19a20555d46c194790c5fbb07c597a"),
        ("frame_16_hex", "41883334120000aa5508000000aa551e"),
        ("xor_ieee_nwk", "7b89f69c798650a0"),
        ("frame_xor_device", "419dbe34101a2b962e94")
    ]

    successful = []

    for i, (desc, token) in enumerate(high_priority, 1):
        print(f"\n[{i:2d}/{len(high_priority)}]", end=" ")
        success, result = test_single_token(token, desc)

        if success:
            successful.append((desc, token, result))
            if 'flag' in str(result).lower():
                return successful

        time.sleep(0.3)

    return successful

def main():
    print("Shadow Coordinator Token Tester")
    print("=" * 50)

    # Test if the API is reachable
    print("🔍 Testing API connectivity...")
    success, result = test_single_token("test", "connectivity_check", verbose=False)

    if "connection_error" in str(result):
        print("❌ Cannot reach API endpoint")
        return
    else:
        print("✅ API endpoint is reachable")

    # First test high priority tokens
    print("\n🎯 Testing high-priority tokens first...")
    high_priority_results = test_specific_tokens()

    if high_priority_results:
        print(f"\n✅ High priority test found {len(high_priority_results)} successful tokens")
        for desc, token, result in high_priority_results:
            if 'flag' in str(result).lower():
                print(f"🚩 FLAG FOUND in high priority test!")
                return

    # Then test all tokens
    print("\n🔄 Testing all generated tokens...")
    all_results = test_all_tokens()

    if not all_results:
        print("\n💡 No tokens worked. Consider:")
        print("   - Check token generation logic")
        print("   - Analyze Frame 307 data further")
        print("   - Try different encoding methods")
        print("   - Check for server-side token format requirements")

if __name__ == "__main__":
    main()