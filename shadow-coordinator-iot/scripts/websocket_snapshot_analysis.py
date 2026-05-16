#!/usr/bin/env python3
"""
Analyze WebSocket snapshot data for coordinator coordinates and flag
We saw: "position": {"x": 400, "y": 240} in earlier WebSocket data
"""
import requests
import json
import websocket
import threading
import time
import ssl

def analyze_coordinates():
    """Analyze the coordinator coordinates from WebSocket snapshot"""
    print("=== COORDINATE ANALYSIS ===")

    # From WebSocket snapshot we saw:
    x, y = 400, 240

    print(f"Coordinator position: x={x}, y={y}")

    # ASCII interpretation
    print(f"X as ASCII: {chr(x) if 32 <= x <= 126 else 'non-printable'}")
    print(f"Y as ASCII: {chr(y) if 32 <= y <= 126 else 'non-printable'}")

    # Hex
    print(f"X as hex: 0x{x:x} ({x:02x})")
    print(f"Y as hex: 0x{y:x} ({y:02x})")

    # Binary
    print(f"X as binary: {bin(x)}")
    print(f"Y as binary: {bin(y)}")

    # Combined interpretations
    coord_bytes = bytes([x % 256, y % 256])  # Take low byte of each
    print(f"Low bytes combined: {coord_bytes}")

    try:
        coord_ascii = coord_bytes.decode('ascii', errors='ignore')
        print(f"Low bytes as ASCII: '{coord_ascii}'")
    except:
        pass

    # Try treating as encoded flag
    potential_flags = [
        f"flag{{{x},{y}}}",
        f"ctf{{{x}_{y}}}",
        f"shadow_coord_{x}_{y}",
        f"coordinator_flag_{x:02x}{y:02x}",
    ]

    print("\nPotential flag formats:")
    for flag in potential_flags:
        print(f"  {flag}")

    # Mathematical analysis
    print(f"\nMathematical analysis:")
    print(f"Sum: {x + y} = {x + y}")
    print(f"Difference: {x - y} = {x - y}")
    print(f"Product: {x * y} = {x * y}")

    # Check if coordinates relate to ASCII values
    if x == 400 and y == 240:  # Our known values
        # 400 in hex = 0x190, 240 in hex = 0xF0
        print(f"Special analysis for {x},{y}:")
        print(f"  400 = 0x190 (decimal 400)")
        print(f"  240 = 0xF0 (decimal 240)")

        # Check for common patterns
        if x % 16 == 0:
            print(f"  X ({x}) is divisible by 16")
        if y % 16 == 0:
            print(f"  Y ({y}) is divisible by 16")

        # Maybe coordinates are hex values to decode?
        try:
            # Try interpreting 400,240 as hex coordinates
            hex_x = f"{x:02x}"  # 190
            hex_y = f"{y:02x}"  # f0

            # Concatenate and try to decode
            hex_combined = hex_x + hex_y  # "190f0"
            print(f"  Hex combined: {hex_combined}")

            # Try as ASCII
            if len(hex_combined) % 2 == 0:
                hex_bytes = bytes.fromhex(hex_combined)
                hex_ascii = hex_bytes.decode('ascii', errors='ignore')
                print(f"  Hex as ASCII: '{hex_ascii}'")

                if any(c.isalnum() for c in hex_ascii):
                    print(f"  [!] Potential text: {hex_ascii}")

        except Exception as e:
            print(f"  Hex decode error: {e}")

def connect_websocket_for_snapshot():
    """Connect to WebSocket to get fresh snapshot data"""
    print("\n=== WEBSOCKET SNAPSHOT CAPTURE ===")

    session = requests.Session()
    session.verify = False
    base_url = "https://training.my-ctf.com:8812"

    # Login
    login_url = "http://training-pod2.ctfchile.com:32780/api/v2/auth/login"
    resp = session.post(login_url, json={"username": "admin", "password": "admin1234"})
    token = resp.json()["access_token"]

    # WebSocket data
    snapshot_data = None

    def on_message(ws, message):
        nonlocal snapshot_data
        try:
            data = json.loads(message)
            if data.get('type') == 'snapshot':
                snapshot_data = data
                print("[+] Snapshot captured!")
                ws.close()
        except:
            pass

    def on_open(ws):
        auth_msg = {"type": "auth", "access_token": token}
        ws.send(json.dumps(auth_msg))

    # Connect
    ws_url = base_url.replace('https://', 'wss://') + "/api/websocket"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_open=on_open
    )

    ws_thread = threading.Thread(target=ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
    ws_thread.daemon = True
    ws_thread.start()

    # Wait for snapshot
    time.sleep(5)
    ws.close()

    if snapshot_data:
        # Extract coordinator position
        nodes = snapshot_data.get('nodes', [])
        coordinator = next((node for node in nodes if node.get('nwk') == '0x0000'), None)

        if coordinator:
            position = coordinator.get('position', {})
            x, y = position.get('x'), position.get('y')

            print(f"[+] Coordinator found at position: {x}, {y}")

            # Look for any flag-like data in the coordinator node
            coord_str = json.dumps(coordinator, indent=2)
            print(f"[+] Full coordinator data:")
            print(coord_str)

            # Check for flags
            if any(keyword in coord_str.lower() for keyword in ['flag', 'ctf', 'shadow']):
                print(f"[!!!] POTENTIAL FLAG IN COORDINATOR DATA:")
                print(coord_str)
                return coord_str

            return position
        else:
            print("[-] No coordinator found in snapshot")
    else:
        print("[-] No snapshot received")

    return None

if __name__ == "__main__":
    # First analyze the coordinates we know
    analyze_coordinates()

    # Then try to get fresh data
    result = connect_websocket_for_snapshot()

    if result and isinstance(result, str) and ('flag' in result.lower() or 'ctf' in result.lower()):
        print(f"\n[!!!] FLAG FOUND: {result}")
    else:
        print(f"\n[INFO] No flag found in coordinate analysis")