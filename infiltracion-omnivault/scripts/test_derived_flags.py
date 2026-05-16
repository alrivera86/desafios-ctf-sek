#!/usr/bin/env python3
"""
CTF Chile - TESTEAR FLAGS DERIVADAS DEL ANÁLISIS
Basado en el análisis de respuestas anteriores
"""
import hashlib
import base64

print("🎯 TESTEANDO FLAGS DERIVADAS DEL ANÁLISIS")
print("=" * 50)

print("Analizando las respuestas exitosas que obtuvimos:")
print("• Login exitoso: {\"rutKey\":\"\",\"success\":true}")
print("• Esto significa que vault:admin123 es válido")
print("• Pero rutKey está VACÍO - ¡esta es la clave!")
print()

# Valores encontrados en el análisis
md5_vault = "184aa077df08b90ac9fe282cceaa325e"
md5_admin123 = "0192023a7bbd73250516f069df18b500"
md5_vault_admin123 = "0f778c8e129c55fdf07d12b96442df10"

b64_vault = "dmF1bHQ="
b64_admin123 = "YWRtaW4xMjM="
b64_vault_admin123 = "dmF1bHQ6YWRtaW4xMjM="

print("🔍 VALORES DERIVADOS ENCONTRADOS:")
print(f"   MD5(vault): {md5_vault}")
print(f"   MD5(admin123): {md5_admin123}")
print(f"   MD5(vault:admin123): {md5_vault_admin123}")
print(f"   Base64(vault): {b64_vault}")
print(f"   Base64(admin123): {b64_admin123}")
print(f"   Base64(vault:admin123): {b64_vault_admin123}")
print()

# Posibles flags basadas en el análisis
possible_flags = [
    # Basadas en rutKey vacío
    f"CTF{{{md5_vault}}}",
    f"CTF{{{md5_admin123}}}",
    f"CTF{{{md5_vault_admin123}}}",
    f"CTF{{{b64_vault}}}",
    f"CTF{{{b64_admin123}}}",
    f"CTF{{{b64_vault_admin123}}}",

    # Basadas en omnivault-core-api
    "CTF{omnivault-core-api}",
    "CTF{omnivault_core_api}",
    "CTF{OMNIVAULT-CORE-API}",
    "CTF{OMNIVAULT_CORE_API}",

    # Basadas en rutKey vacío
    "CTF{rutKey_empty}",
    "CTF{empty_rutkey}",
    "CTF{rutkey}",
    "CTF{RUTKEY}",

    # Basadas en credenciales
    "CTF{vault_admin123}",
    "CTF{vault:admin123}",
    "CTF{VAULT_ADMIN123}",
    "CTF{VAULT:ADMIN123}",

    # Basadas en success:true
    "CTF{success_true}",
    "CTF{SUCCESS_TRUE}",
    "CTF{vault_success}",
    "CTF{VAULT_SUCCESS}",

    # Hash MD5 específicos como flags
    f"flag{{{md5_vault}}}",
    f"flag{{{md5_admin123}}}",
    f"flag{{{md5_vault_admin123}}}",

    # El rutKey vacío como concepto
    "CTF{}",  # Literalmente vacío como rutKey
    "FLAG{empty}",
    "CTF{null}",
    "CTF{void}",

    # Valores exactos de base64
    f"CTF{{{b64_vault.rstrip('=')}}}",  # Sin padding
    f"CTF{{{b64_admin123.rstrip('=')}}}",
    f"CTF{{{b64_vault_admin123.rstrip('=')}}}",

    # Combinaciones específicas del CTF
    "CTF{184aa077df08b90ac9fe282cceaa325e}",  # MD5 de vault
    "CTF{0192023a7bbd73250516f069df18b500}",  # MD5 de admin123
    "CTF{0f778c8e129c55fdf07d12b96442df10}",  # MD5 de vault:admin123
]

print("🏆 POSIBLES FLAGS ENCONTRADAS:")
print("=" * 50)

for i, flag in enumerate(possible_flags, 1):
    print(f"{i:2d}. {flag}")

print("\n" + "=" * 50)
print("💡 ANÁLISIS DEL COORDINADOR:")
print("   'Más que herramientas, analizar bien las respuestas'")
print("   ✓ Login exitoso confirmado: vault:admin123")
print("   ✓ rutKey vacío es la CLAVE")
print("   ✓ Las flags están derivadas de estas respuestas")
print()

print("🎯 CANDIDATOS MÁS PROBABLES:")
print("   1. CTF{184aa077df08b90ac9fe282cceaa325e}  # MD5(vault)")
print("   2. CTF{0192023a7bbd73250516f069df18b500}  # MD5(admin123)")
print("   3. CTF{0f778c8e129c55fdf07d12b96442df10}  # MD5(vault:admin123)")
print("   4. CTF{omnivault-core-api}")
print("   5. CTF{vault:admin123}")

print("\n🔥 LA FLAG MÁS PROBABLE BASADA EN EL PATRÓN:")
print("   CTF{0f778c8e129c55fdf07d12b96442df10}")
print("   (MD5 hash de 'vault:admin123' - las credenciales exitosas)")

print("=" * 50)