#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS PROFUNDO DE RESPUESTAS ANTERIORES
El coordinador dice que hay que analizar mejor las respuestas
"""
import requests
import re
import base64
import json

TARGET = "http://training-pod2.ctfchile.com:32778"

print("🔍 ANÁLISIS PROFUNDO DE RESPUESTAS DEL CTF")
print("=" * 50)

def analyze_response(response_text, source):
    """Analiza una respuesta en busca de flags ocultas"""
    print(f"\n📋 Analizando respuesta de: {source}")
    print(f"   Longitud: {len(response_text)} chars")

    # 1. Buscar flags obvias
    flag_patterns = [
        r'CTF\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'flag\{[^}]+\}',
        r'chile\{[^}]+\}'
    ]

    for pattern in flag_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        if matches:
            print(f"   🏆 FLAG DIRECTA: {matches[0]}")
            return matches[0]

    # 2. Buscar texto codificado en base64
    b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', response_text)
    for b64 in b64_patterns:
        try:
            decoded = base64.b64decode(b64).decode('utf-8', 'ignore')
            print(f"   🔓 Base64 decodificado: {decoded[:100]}...")
            for pattern in flag_patterns:
                matches = re.findall(pattern, decoded, re.IGNORECASE)
                if matches:
                    print(f"   🏆 FLAG EN BASE64: {matches[0]}")
                    return matches[0]
        except:
            pass

    # 3. Buscar rutKey u otros valores específicos
    try:
        if response_text.startswith('{'):
            json_data = json.loads(response_text)
            print(f"   📊 JSON keys: {list(json_data.keys())}")

            # Buscar rutKey específicamente
            if 'rutKey' in json_data and json_data['rutKey']:
                print(f"   🔑 rutKey encontrada: {json_data['rutKey']}")

                # Decodificar rutKey si parece base64
                rutkey = json_data['rutKey']
                if len(rutkey) > 10:
                    try:
                        decoded_rut = base64.b64decode(rutkey).decode('utf-8', 'ignore')
                        print(f"   🔓 rutKey decodificada: {decoded_rut}")
                        for pattern in flag_patterns:
                            matches = re.findall(pattern, decoded_rut, re.IGNORECASE)
                            if matches:
                                print(f"   🏆 FLAG EN rutKey: {matches[0]}")
                                return matches[0]
                    except:
                        pass
    except:
        pass

    # 4. Buscar patrones ocultos en el texto
    hidden_patterns = [
        r'<!--.*?-->', # Comentarios HTML
        r'/\*.*?\*/', # Comentarios CSS/JS
        r'//.*?\n', # Comentarios línea
        r'"[A-Za-z0-9+/=]{20,}"' # Strings que parecen base64
    ]

    for pattern in hidden_patterns:
        matches = re.findall(pattern, response_text, re.DOTALL)
        for match in matches:
            print(f"   💭 Contenido oculto: {match[:50]}...")
            for flag_pattern in flag_patterns:
                flag_matches = re.findall(flag_pattern, match, re.IGNORECASE)
                if flag_matches:
                    print(f"   🏆 FLAG OCULTA: {flag_matches[0]}")
                    return flag_matches[0]

    return None

print("[1] Re-analizando login exitoso...")

# Volver a hacer el login y analizar la respuesta completa
try:
    login_response = requests.post(f"{TARGET}/api/login",
                                 headers={"Content-Type": "application/json"},
                                 json={"username": "vault", "password": "admin123"},
                                 timeout=10)

    print(f"   Status: {login_response.status_code}")
    print(f"   Headers: {dict(login_response.headers)}")
    print(f"   Cookies: {dict(login_response.cookies)}")

    # Analizar respuesta completa
    flag = analyze_response(login_response.text, "LOGIN vault:admin123")
    if flag:
        print(f"\n🎯 FLAG ENCONTRADA EN LOGIN: {flag}")

    # Analizar headers
    for header, value in login_response.headers.items():
        flag = analyze_response(value, f"HEADER {header}")
        if flag:
            print(f"\n🎯 FLAG EN HEADER {header}: {flag}")

except Exception as e:
    print(f"   Error en login: {e}")

print(f"\n[2] Analizando página principal completa...")

try:
    main_response = requests.get(TARGET, timeout=10)
    flag = analyze_response(main_response.text, "PÁGINA PRINCIPAL")
    if flag:
        print(f"\n🎯 FLAG EN PÁGINA PRINCIPAL: {flag}")

    # Analizar el código fuente línea por línea
    lines = main_response.text.split('\n')
    for i, line in enumerate(lines):
        if 'flag' in line.lower() or 'ctf' in line.lower():
            print(f"   📝 Línea {i+1}: {line.strip()}")
            flag = analyze_response(line, f"LÍNEA {i+1}")
            if flag:
                print(f"\n🎯 FLAG EN LÍNEA {i+1}: {flag}")

except Exception as e:
    print(f"   Error en página principal: {e}")

print(f"\n[3] Probando endpoints específicos encontrados...")

# Endpoints que sabemos que existen
endpoints = [
    "/dashboard.html",
    "/2fa.html",
    "/api/section/flag",
    "/api/user/profile"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{TARGET}{endpoint}", timeout=5)
        if response.status_code == 200:
            flag = analyze_response(response.text, f"GET {endpoint}")
            if flag:
                print(f"\n🎯 FLAG EN {endpoint}: {flag}")
    except:
        pass

print("=" * 50)
print("💡 Tip del coordinador: 'Analizar bien las respuestas'")
print("🔍 Revisión completa de todas las respuestas anteriores terminada")