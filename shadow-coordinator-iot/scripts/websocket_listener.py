#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys

async def listen_websocket():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJvd25lciIsIm5hbWUiOiJBZG1pbiIsImlhdCI6MTc3ODc3Mzg2NywiZXhwIjoxNzc4ODAyNjY3fQ.zIn7IaxtnY9b8HJyWWwS15PZ4G7SaZyQMgmoTzuXPoE"
    uri = "ws://training-pod2.ctfchile.com:32780/api/websocket"

    try:
        async with websockets.connect(uri) as websocket:
            print("[+] Connected to WebSocket")

            # Wait for auth_required
            auth_msg = await websocket.recv()
            print(f"[*] Received: {auth_msg}")

            # Send auth with token
            auth_data = {"type": "auth", "access_token": token}
            await websocket.send(json.dumps(auth_data))

            # Get auth response
            auth_response = await websocket.recv()
            print(f"[*] Auth response: {auth_response}")

            auth_resp_data = json.loads(auth_response)
            if auth_resp_data.get('type') != 'auth_ok':
                print("[-] Authentication failed")
                return

            print("[+] Authentication successful! Listening for events...")

            # Subscribe to events
            await websocket.send(json.dumps({"type": "subscribe_events", "event_type": "state_changed"}))

            # Listen for messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    msg_data = json.loads(message)

                    print(f"\n[*] Event: {msg_data.get('type', 'unknown')}")
                    if 'event' in msg_data:
                        event = msg_data['event']
                        print(f"    Event type: {event.get('event_type', 'N/A')}")
                        if 'data' in event:
                            print(f"    Data: {json.dumps(event['data'], indent=6)}")
                    elif 'type' in msg_data:
                        if msg_data['type'] == 'service_executed':
                            print(f"    Service executed: {json.dumps(msg_data, indent=6)}")
                        elif msg_data['type'] in ['result', 'error']:
                            print(f"    Result: {json.dumps(msg_data, indent=6)}")
                        else:
                            print(f"    Message: {json.dumps(msg_data, indent=6)}")

                except asyncio.TimeoutError:
                    print("[*] No messages received in 30 seconds, continuing...")
                    continue
                except Exception as e:
                    print(f"[*] Error processing message: {e}")

    except Exception as e:
        print(f"[-] WebSocket error: {e}")

if __name__ == "__main__":
    print("[*] Starting WebSocket listener for flag extraction...")
    asyncio.run(listen_websocket())