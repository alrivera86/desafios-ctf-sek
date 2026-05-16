#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://training-pod2.ctfchile.com:32780/api/websocket"

    try:
        async with websockets.connect(uri) as websocket:
            print("[+] Connected to WebSocket")

            # Listen for auth_required
            auth_msg = await websocket.recv()
            print(f"[*] Received: {auth_msg}")

            # Try different auth approaches
            auth_attempts = [
                {"type": "auth", "access_token": "admin1234"},
                {"type": "auth", "access_token": "bearer_admin1234"},
                {"type": "auth", "access_token": ""},
                {"type": "auth", "username": "admin", "password": "admin1234"},
                {"type": "auth_plain", "username": "admin", "password": "admin1234"},
            ]

            for attempt in auth_attempts:
                print(f"\n[*] Trying auth: {attempt}")
                await websocket.send(json.dumps(attempt))

                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    print(f"[*] Response: {response}")

                    resp_data = json.loads(response)
                    if resp_data.get('type') == 'auth_ok':
                        print("[+] Authentication successful!")

                        # Try to subscribe to events
                        await websocket.send(json.dumps({"type": "subscribe_events", "event_type": "state_changed"}))

                        # Listen for more messages
                        for i in range(5):
                            try:
                                msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                                print(f"[*] Event {i}: {msg}")
                            except asyncio.TimeoutError:
                                break
                        return

                except asyncio.TimeoutError:
                    print("[*] No response (timeout)")
                except Exception as e:
                    print(f"[*] Error: {e}")

            print("[-] All authentication attempts failed")

    except Exception as e:
        print(f"[-] WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())