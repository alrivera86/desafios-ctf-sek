#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS COMPLETO DEL CÓDIGO FUENTE
Buscando en archivos JS, CSS y código HTML completo
"""
import requests
import re
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"

print("📋 ANÁLISIS COMPLETO DEL CÓDIGO FUENTE")
print("=" * 50)

def search_flags_in_text(text, source_name):
    """Buscar flags en cualquier texto"""
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']

    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"   🏆 FLAG EN {source_name}: {matches[0]}")
            return matches[0]

    return None

def analyze_main_html():
    """Análisis completo del HTML principal"""
    print("[1] Descargando y analizando HTML completo...")

    try:
        response = requests.get(TARGET, timeout=10)
        html_content = response.text

        print(f"   📄 HTML completo ({len(html_content)} chars)")

        # Buscar flag directamente en HTML
        flag = search_flags_in_text(html_content, "HTML PRINCIPAL")
        if flag:
            return flag

        # Extraer todas las referencias a archivos
        print(f"\n   🔗 Extrayendo referencias a archivos...")

        # JavaScript files
        js_files = re.findall(r'<script.*?src=[\'"]([^\'"]+)[\'"]', html_content, re.IGNORECASE)
        print(f"   📜 Archivos JavaScript encontrados:")
        for js_file in js_files:
            print(f"      • {js_file}")

        # CSS files
        css_files = re.findall(r'<link.*?href=[\'"]([^\'"]+\.css[^\'"]*)[\'"]', html_content, re.IGNORECASE)
        print(f"   🎨 Archivos CSS encontrados:")
        for css_file in css_files:
            print(f"      • {css_file}")

        # Otros archivos
        other_files = re.findall(r'(?:src|href)=[\'"]([^\'"]+\.(png|jpg|jpeg|gif|ico|json|xml|txt))[\'"]', html_content, re.IGNORECASE)
        print(f"   📁 Otros archivos encontrados:")
        for file_match in other_files:
            print(f"      • {file_match[0]}")

        # Analizar comentarios específicos
        print(f"\n   💭 Analizando comentarios específicos...")
        comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
        for i, comment in enumerate(comments, 1):
            comment_clean = comment.strip()
            print(f"      Comentario {i}: {comment_clean[:100]}...")

            flag = search_flags_in_text(comment_clean, f"COMENTARIO {i}")
            if flag:
                return flag

            # Decodificar si parece base64
            words = comment_clean.split()
            for word in words:
                if len(word) > 10:
                    try:
                        decoded = base64.b64decode(word + "==").decode('utf-8', 'ignore')
                        flag = search_flags_in_text(decoded, f"COMENTARIO {i} DECODIFICADO")
                        if flag:
                            return flag
                    except:
                        pass

        # Analizar JavaScript inline
        print(f"\n   💻 Analizando JavaScript inline...")
        js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
        for i, js_block in enumerate(js_blocks, 1):
            print(f"      JS Block {i}: {js_block.strip()[:100]}...")
            flag = search_flags_in_text(js_block, f"JAVASCRIPT INLINE {i}")
            if flag:
                return flag

        # Buscar strings interesantes
        print(f"\n   🔍 Buscando strings interesantes...")

        # IDs y classes que podrían ser pistas
        ids = re.findall(r'id=[\'"]([^\'"]+)[\'"]', html_content)
        classes = re.findall(r'class=[\'"]([^\'"]+)[\'"]', html_content)

        print(f"      IDs interesantes:")
        for id_val in set(ids):
            if any(keyword in id_val.lower() for keyword in ['flag', 'ctf', 'chile', 'secret']):
                print(f"         • {id_val}")
                flag = search_flags_in_text(id_val, f"ID {id_val}")
                if flag:
                    return flag

        print(f"      Classes interesantes:")
        for class_val in set(classes):
            if any(keyword in class_val.lower() for keyword in ['flag', 'ctf', 'chile', 'secret']):
                print(f"         • {class_val}")
                flag = search_flags_in_text(class_val, f"CLASS {class_val}")
                if flag:
                    return flag

        return None, js_files, css_files, other_files

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, [], [], []

def download_and_analyze_files(files, file_type):
    """Descargar y analizar archivos específicos"""

    for file_path in files:
        try:
            # Construir URL completa
            if file_path.startswith('http'):
                url = file_path
            else:
                url = f"{TARGET}/{file_path.lstrip('/')}"

            print(f"\n   📥 Descargando {file_type}: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                content = response.text
                print(f"      Tamaño: {len(content)} chars")
                print(f"      Contenido: {content[:100]}...")

                flag = search_flags_in_text(content, f"{file_type} {file_path}")
                if flag:
                    return flag

                # Para JavaScript, buscar variables interesantes
                if file_type == "JS":
                    variables = re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                    for var_name, var_value in variables:
                        if any(keyword in var_name.lower() for keyword in ['flag', 'ctf', 'chile', 'secret']):
                            print(f"         Variable interesante: {var_name} = {var_value}")
                            flag = search_flags_in_text(var_value, f"VARIABLE {var_name}")
                            if flag:
                                return flag
            else:
                print(f"      ❌ Error {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error descargando {file_path}: {e}")

    return None

# ANÁLISIS PRINCIPAL
print("Analizando código fuente completo de la aplicación...")

# Analizar HTML principal
result = analyze_main_html()
if isinstance(result, tuple):
    flag, js_files, css_files, other_files = result
else:
    flag = result
    js_files, css_files, other_files = [], [], []

if flag:
    print(f"\n🎉 FLAG ENCONTRADA: {flag}")
else:
    print(f"\n[2] Analizando archivos JavaScript...")
    flag = download_and_analyze_files(js_files, "JS")

    if not flag:
        print(f"\n[3] Analizando archivos CSS...")
        flag = download_and_analyze_files(css_files, "CSS")

    if not flag:
        print(f"\n[4] Analizando otros archivos...")
        flag = download_and_analyze_files([f[0] for f in other_files], "OTHER")

# Si aún no encontramos nada, probar archivos comunes
if not flag:
    print(f"\n[5] Probando archivos comunes...")
    common_files = [
        "robots.txt",
        "sitemap.xml",
        "flag.txt",
        "flag.js",
        "config.js",
        "app.js",
        "main.js",
        "index.js",
        "secret.txt",
        "ctf.txt",
        ".well-known/flag",
        "admin/flag.txt",
        "static/flag.txt"
    ]

    flag = download_and_analyze_files(common_files, "COMMON")

if flag:
    print(f"\n" + "="*50)
    print(f"🎉 FLAG ENCONTRADA: {flag}")
    print(f"="*50)
else:
    print(f"\n" + "="*50)
    print("❌ No se encontró flag en código fuente")
    print("💡 La flag podría estar en:")
    print("   1. Una API específica que requiere autenticación")
    print("   2. Generada dinámicamente por JavaScript")
    print("   3. En el backend, accesible solo por RCE")
    print("   4. Codificada de forma que no reconocemos")
    print("="*50)