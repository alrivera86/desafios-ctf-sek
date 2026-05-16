#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS PROFUNDO DE HEADERS, COOKIES Y DETALLES OCULTOS
Buscando en lugares menos obvios
"""
import requests
import re
import base64
import time

TARGET = "http://training-pod2.ctfchile.com:32785"

print("🔍 BÚSQUEDA EN LUGARES OCULTOS")
print("=" * 50)
print("💡 Analizando headers, cookies, timing, y detalles ocultos")
print()

def search_flags_everywhere(response, source):
    """Buscar flags en TODOS los aspectos de la respuesta"""
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']

    found_flags = []

    # 1. En el body (ya lo hemos hecho, pero por completitud)
    print(f"   📄 Body: {response.text[:100]}...")
    for pattern in flag_patterns:
        matches = re.findall(pattern, response.text, re.IGNORECASE)
        if matches:
            found_flags.extend(matches)

    # 2. En TODOS los headers
    print(f"   📋 Headers completos:")
    for header, value in response.headers.items():
        print(f"      {header}: {value}")
        for pattern in flag_patterns:
            matches = re.findall(pattern, value, re.IGNORECASE)
            if matches:
                found_flags.extend(matches)

    # 3. En cookies
    print(f"   🍪 Cookies: {dict(response.cookies)}")
    for cookie_name, cookie_value in response.cookies.items():
        print(f"      Cookie {cookie_name}: {cookie_value}")
        for pattern in flag_patterns:
            matches = re.findall(pattern, f"{cookie_name}={cookie_value}", re.IGNORECASE)
            if matches:
                found_flags.extend(matches)

    # 4. En status code como número
    print(f"   📊 Status Code: {response.status_code}")
    status_flags = [
        f"CTF{{{response.status_code}}}",
        f"flag{{{response.status_code}}}",
        f"CTF{{status_{response.status_code}}}",
    ]
    print(f"      Posibles flags del status: {status_flags}")

    # 5. En el tamaño de respuesta
    content_length = len(response.text)
    print(f"   📏 Tamaño respuesta: {content_length} chars")
    length_flags = [
        f"CTF{{{content_length}}}",
        f"flag{{{content_length}}}",
    ]
    print(f"      Posibles flags del tamaño: {length_flags}")

    # 6. En URL de respuesta (redirects, etc.)
    print(f"   🔗 URL final: {response.url}")
    for pattern in flag_patterns:
        matches = re.findall(pattern, response.url, re.IGNORECASE)
        if matches:
            found_flags.extend(matches)

    # 7. En valores base64 ocultos en headers
    for header, value in response.headers.items():
        if len(value) > 10:
            try:
                decoded = base64.b64decode(value + "==").decode('utf-8', 'ignore')
                for pattern in flag_patterns:
                    matches = re.findall(pattern, decoded, re.IGNORECASE)
                    if matches:
                        print(f"      🔓 Flag en header {header} decodificado: {matches[0]}")
                        found_flags.extend(matches)
            except:
                pass

    if found_flags:
        print(f"   🏆 FLAGS ENCONTRADAS en {source}: {found_flags}")
        return found_flags[0]

    return None

def analyze_main_page():
    """Análisis completo de la página principal"""
    print("[1] Análisis completo de página principal...")

    try:
        start_time = time.time()
        response = requests.get(TARGET, timeout=10)
        end_time = time.time()

        print(f"   ⏱️  Tiempo de respuesta: {end_time - start_time:.3f} segundos")

        # Buscar flags en todos los aspectos
        flag = search_flags_everywhere(response, "PÁGINA PRINCIPAL")
        if flag:
            return flag

        # Buscar en comentarios HTML específicamente
        print(f"   💭 Buscando en comentarios HTML...")
        html_comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
        for i, comment in enumerate(html_comments):
            print(f"      Comentario {i+1}: {comment.strip()[:50]}...")
            for pattern in [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']:
                matches = re.findall(pattern, comment, re.IGNORECASE)
                if matches:
                    print(f"      🏆 FLAG EN COMENTARIO: {matches[0]}")
                    return matches[0]

        # Buscar en JavaScript inline
        print(f"   💻 Buscando en JavaScript...")
        js_blocks = re.findall(r'<script.*?>(.*?)</script>', response.text, re.DOTALL | re.IGNORECASE)
        for i, js in enumerate(js_blocks):
            print(f"      JS Block {i+1}: {js.strip()[:50]}...")
            for pattern in [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']:
                matches = re.findall(pattern, js, re.IGNORECASE)
                if matches:
                    print(f"      🏆 FLAG EN JAVASCRIPT: {matches[0]}")
                    return matches[0]

        # Buscar strings que parezcan flags pero sin CTF{}
        print(f"   🔍 Buscando patrones similares a flags...")
        potential_flags = re.findall(r'\b[a-f0-9]{32}\b', response.text)  # MD5 hashes
        potential_flags.extend(re.findall(r'\b[a-f0-9]{40}\b', response.text))  # SHA1 hashes

        for potential in potential_flags:
            print(f"      Hash encontrado: {potential}")
            test_flag = f"CTF{{{potential}}}"
            print(f"      Posible flag: {test_flag}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    return None

def analyze_flag_endpoint():
    """Análisis completo del endpoint flag"""
    print(f"\n[2] Análisis completo del endpoint /api/section/flag...")

    try:
        start_time = time.time()
        response = requests.get(f"{TARGET}/api/section/flag", timeout=10)
        end_time = time.time()

        print(f"   ⏱️  Tiempo de respuesta: {end_time - start_time:.3f} segundos")

        flag = search_flags_everywhere(response, "ENDPOINT FLAG")
        if flag:
            return flag

        # Probar con diferentes User-Agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "CTF-Bot/1.0",
            "flag-hunter",
            "Chile-CTF-2024"
        ]

        for ua in user_agents:
            try:
                response = requests.get(f"{TARGET}/api/section/flag",
                                      headers={"User-Agent": ua},
                                      timeout=5)
                if response.text != '{"section":"flag","message":"Contenido cargado exitosamente","status":"ok"}':
                    print(f"      🆕 Respuesta diferente con UA {ua}: {response.text}")
                    flag = search_flags_everywhere(response, f"UA {ua}")
                    if flag:
                        return flag
            except:
                pass

    except Exception as e:
        print(f"   ❌ Error: {e}")

    return None

def check_specific_headers():
    """Verificar headers específicos que podrían contener flags"""
    print(f"\n[3] Verificando headers específicos...")

    custom_headers = {
        "X-Flag": "show",
        "X-CTF": "true",
        "X-Chile": "ctf",
        "Flag": "show",
        "CTF": "true",
        "Show-Flag": "true",
        "Content-Type": "application/flag"
    }

    try:
        response = requests.get(f"{TARGET}/api/section/flag", headers=custom_headers, timeout=10)
        flag = search_flags_everywhere(response, "CUSTOM HEADERS")
        if flag:
            return flag

    except Exception as e:
        print(f"   ❌ Error: {e}")

    return None

# ANÁLISIS PRINCIPAL
flag_found = None

flag_found = analyze_main_page()
if not flag_found:
    flag_found = analyze_flag_endpoint()
if not flag_found:
    flag_found = check_specific_headers()

if flag_found:
    print(f"\n" + "="*50)
    print(f"🎉 FLAG ENCONTRADA: {flag_found}")
    print(f"="*50)
else:
    print(f"\n" + "="*50)
    print("❌ No se encontró flag en análisis profundo")
    print("\n💡 LUGARES DONDE PODRÍA ESTAR LA FLAG:")
    print("   1. En un header HTTP específico que no probé")
    print("   2. En el timing exacto de las respuestas")
    print("   3. En una secuencia específica de requests")
    print("   4. En información del servidor (Server header)")
    print("   5. En el código fuente de la página principal")
    print("   6. En algún archivo estático (.css, .js)")
    print("\n🔍 PRÓXIMO PASO: Revisar manualmente el código fuente")
    print("   Ve a: http://training-pod2.ctfchile.com:32785")
    print("   Y presiona F12 -> Sources para ver todos los archivos")
    print("="*50)