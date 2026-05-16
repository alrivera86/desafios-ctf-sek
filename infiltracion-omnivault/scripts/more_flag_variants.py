#!/usr/bin/env python3
"""
CTF Chile - MÁS VARIANTES DE FLAGS
Explorando otros patrones comunes de CTFs
"""
import hashlib
import base64

print("🔄 GENERANDO MÁS VARIANTES DE FLAGS")
print("=" * 50)

# Datos base
username = "vault"
password = "admin123"
combined = f"{username}:{password}"
combined_no_colon = f"{username}{password}"

print("📊 Datos base:")
print(f"   Usuario: {username}")
print(f"   Password: {password}")
print(f"   Combinado: {combined}")
print()

def generate_hashes(text, label):
    """Genera diferentes tipos de hash para un texto"""
    print(f"🔐 Hashes para '{text}' ({label}):")

    hashes = {}

    # MD5
    hashes['md5'] = hashlib.md5(text.encode()).hexdigest()
    print(f"   MD5: {hashes['md5']}")

    # SHA1
    hashes['sha1'] = hashlib.sha1(text.encode()).hexdigest()
    print(f"   SHA1: {hashes['sha1']}")

    # SHA256
    hashes['sha256'] = hashlib.sha256(text.encode()).hexdigest()
    print(f"   SHA256: {hashes['sha256'][:32]}... (truncado)")

    # Base64
    hashes['b64'] = base64.b64encode(text.encode()).decode()
    print(f"   Base64: {hashes['b64']}")

    # Hex
    hashes['hex'] = text.encode().hex()
    print(f"   Hex: {hashes['hex']}")

    print()
    return hashes

# Generar hashes para diferentes combinaciones
vault_hashes = generate_hashes(username, "usuario")
admin_hashes = generate_hashes(password, "password")
combined_hashes = generate_hashes(combined, "usuario:password")
combined_no_colon_hashes = generate_hashes(combined_no_colon, "usuariopassword")

# Generar flags
all_flags = []

print("🏆 GENERANDO TODAS LAS POSIBLES FLAGS:")
print("=" * 50)

# Formato CTF{hash}
for label, hash_dict in [
    ("vault", vault_hashes),
    ("admin123", admin_hashes),
    ("vault:admin123", combined_hashes),
    ("vaultadmin123", combined_no_colon_hashes)
]:
    print(f"\n📋 FLAGS basadas en '{label}':")
    for hash_type, hash_value in hash_dict.items():
        flag = f"CTF{{{hash_value}}}"
        all_flags.append(flag)
        print(f"   • CTF{{{hash_value}}} ({hash_type})")

# Formato flag{hash}
print(f"\n📋 FLAGS con formato 'flag{{}}':")
for label, hash_dict in [("vault:admin123", combined_hashes)]:
    for hash_type, hash_value in hash_dict.items():
        flag = f"flag{{{hash_value}}}"
        all_flags.append(flag)
        print(f"   • flag{{{hash_value}}} ({hash_type})")

# Flags textuales específicas
textual_flags = [
    "CTF{vault}",
    "CTF{admin123}",
    "CTF{vault:admin123}",
    "CTF{vaultadmin123}",
    "CTF{VAULT}",
    "CTF{ADMIN123}",
    "CTF{VAULT:ADMIN123}",
    "CTF{VAULTADMIN123}",
    "flag{vault}",
    "flag{admin123}",
    "flag{vault:admin123}",
    "FLAG{VAULT}",
    "FLAG{ADMIN123}",
    "FLAG{VAULT:ADMIN123}",

    # Específicas del sistema
    "CTF{omnivault}",
    "CTF{OMNIVAULT}",
    "CTF{omnivault-core-api}",
    "CTF{OMNIVAULT-CORE-API}",
    "CTF{omnivault_core_api}",
    "CTF{OMNIVAULT_CORE_API}",

    # Basadas en rutKey
    "CTF{rutkey}",
    "CTF{RUTKEY}",
    "CTF{rutKey}",
    "CTF{rut_key}",
    "CTF{RUT_KEY}",
    "CTF{empty_rutkey}",
    "CTF{EMPTY_RUTKEY}",
    "CTF{rutkey_empty}",
    "CTF{RUTKEY_EMPTY}",

    # Success patterns
    "CTF{success}",
    "CTF{SUCCESS}",
    "CTF{success_true}",
    "CTF{SUCCESS_TRUE}",
    "CTF{vault_success}",
    "CTF{VAULT_SUCCESS}",

    # Chile specific
    "CTF{chile}",
    "CTF{CHILE}",
    "flag{chile}",
    "FLAG{CHILE}",
    "CTF{ctfchile}",
    "CTF{CTFCHILE}",
]

print(f"\n📋 FLAGS textuales específicas:")
for flag in textual_flags:
    all_flags.append(flag)
    print(f"   • {flag}")

# Variaciones con números
print(f"\n📋 FLAGS con variaciones numéricas:")
numeric_variants = [
    "CTF{vault123}",
    "CTF{admin}",
    "CTF{vault_123}",
    "CTF{admin_123}",
    "CTF{123vault}",
    "CTF{123admin}",
    "CTF{vault2024}",
    "CTF{admin2024}",
    "flag{123}",
    "CTF{training}",
    "CTF{pod2}",
    "CTF{32778}",
]

for flag in numeric_variants:
    all_flags.append(flag)
    print(f"   • {flag}")

print(f"\n" + "=" * 50)
print(f"📊 TOTAL DE FLAGS GENERADAS: {len(all_flags)}")
print(f"=" * 50)

print(f"\n🎯 TOP 10 CANDIDATOS MÁS PROBABLES:")
top_candidates = [
    f"CTF{{{combined_hashes['sha1']}}}", # SHA1 de vault:admin123
    f"CTF{{{vault_hashes['sha1']}}}", # SHA1 de vault
    f"CTF{{{combined_hashes['md5']}}}", # MD5 de vault:admin123 (ya probado)
    "CTF{vault:admin123}",
    "CTF{omnivault-core-api}",
    f"CTF{{{combined_hashes['b64']}}}", # Base64 de vault:admin123
    "CTF{rutkey}",
    "CTF{success}",
    f"CTF{{{combined_no_colon_hashes['md5']}}}", # MD5 de vaultadmin123
    "CTF{VAULT:ADMIN123}"
]

for i, flag in enumerate(top_candidates, 1):
    print(f"   {i:2d}. {flag}")

print(f"\n🔥 PRÓXIMA FLAG A PROBAR:")
print(f"   CTF{{{combined_hashes['sha1']}}}")
print(f"   (SHA1 de 'vault:admin123')")

print(f"\n💡 Si no funciona, prueba en orden:")
print("   1. Flags con SHA1")
print("   2. Flags textuales (CTF{vault:admin123})")
print("   3. Flags del sistema (CTF{omnivault})")
print("   4. Flags con Base64")

print("=" * 50)