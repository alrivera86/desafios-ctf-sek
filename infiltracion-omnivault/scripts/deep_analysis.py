#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS PROFUNDO DE RESPUESTAS OBTENIDAS
Analizando respuestas específicas que ya obtuvimos
"""
import re
import base64
import json
import hashlib

print("🔍 ANÁLISIS PROFUNDO DE RESPUESTAS ANTERIORES")
print("=" * 55)

# Respuestas específicas que obtuvimos en ejecuciones anteriores
responses_found = [
    '{"rutKey":"","success":true}',  # Login exitoso
    '{"success":false,"module":"omnivault-core-api","error":"Internal Server Error","message":"An unexpected error occurred while processing your request.","status":500}',
    '{"success":false,"message":"Clave Digital incorrecta."}',
    '{"success":false,"error":"Unknown Error","message":"System failure. Please contact support.","status":500}',
    '{"success":false,"error":"Not Found","message":"The requested endpoint does not exist in OmniVault Internal Router.","status":404}'
]

def analyze_deep(text, source):
    print(f"\n📋 Analizando: {source}")
    print(f"   Texto: {text}")

    # 1. Flags directas
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']
    for pattern in flag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"   🏆 FLAG DIRECTA: {matches[0]}")
            return matches[0]

    # 2. Analizar JSON
    try:
        data = json.loads(text)
        print(f"   📊 Estructura JSON: {list(data.keys())}")

        # 3. Analizar cada valor
        for key, value in data.items():
            print(f"   🔑 {key}: '{value}'")

            # El rutKey vacío podría ser significativo
            if key == "rutKey" and value == "":
                print(f"   💡 rutKey vacío - esto podría ser intencional")

                # ¿Qué pasaría si combinamos vault + admin123?
                possible_rutkeys = [
                    "vault",
                    "admin123",
                    "vaultadmin123",
                    "admin123vault",
                    hashlib.md5(b"vault").hexdigest(),
                    hashlib.md5(b"admin123").hexdigest(),
                    hashlib.md5(b"vault:admin123").hexdigest(),
                    base64.b64encode(b"vault").decode(),
                    base64.b64encode(b"admin123").decode(),
                    base64.b64encode(b"vault:admin123").decode(),
                ]

                print(f"   🔧 Posibles rutKeys derivados:")
                for rutkey in possible_rutkeys:
                    print(f"      - {rutkey}")

                    # Decodificar si parece base64
                    if len(rutkey) > 8:
                        try:
                            decoded = base64.b64decode(rutkey + "==").decode('utf-8', 'ignore')
                            for pattern in flag_patterns:
                                matches = re.findall(pattern, decoded, re.IGNORECASE)
                                if matches:
                                    print(f"   🏆 FLAG EN rutKey decodificado {rutkey}: {matches[0]}")
                                    return matches[0]
                        except:
                            pass

            # Analizar mensajes de error
            if "message" in key or "error" in key:
                # ¿Hay algo oculto en los mensajes?
                if "omnivault-core-api" in str(value):
                    print(f"   💡 Módulo específico mencionado: omnivault-core-api")

                if "An unexpected error occurred" in str(value):
                    print(f"   💡 Error genérico - podría ocultar información")

                # Buscar patrones ocultos en mensajes
                hidden_text = str(value)
                # ROT13
                try:
                    import codecs
                    rot13 = codecs.encode(hidden_text, 'rot13')
                    for pattern in flag_patterns:
                        matches = re.findall(pattern, rot13, re.IGNORECASE)
                        if matches:
                            print(f"   🏆 FLAG EN ROT13: {matches[0]}")
                            return matches[0]
                except:
                    pass
    except:
        pass

    # 4. Buscar patrones específicos del CTF
    if "vault" in text.lower():
        print(f"   🔐 Mención de 'vault' detectada")

    if "admin123" in text.lower():
        print(f"   🔑 Mención de 'admin123' detectada")

    if "success" in text.lower() and "true" in text.lower():
        print(f"   ✅ Operación exitosa confirmada")

    return None

print("[1] Analizando respuesta de login exitoso...")
flag = analyze_deep('{"rutKey":"","success":true}', "LOGIN EXITOSO")
if flag:
    print(f"\n🎯 FLAG ENCONTRADA: {flag}")

print("\n[2] Analizando errores específicos...")
for i, response in enumerate(responses_found[1:], 2):
    flag = analyze_deep(response, f"RESPUESTA {i}")
    if flag:
        print(f"\n🎯 FLAG ENCONTRADA EN RESPUESTA {i}: {flag}")

print("\n[3] Análisis de patrones específicos...")

# El coordinador dice que hay que analizar las respuestas mejor
# ¿Podría ser que la flag esté en la AUSENCIA de algo?
print("\n💭 Análisis de ausencias...")
print("   • rutKey está vacío en login exitoso")
print("   • Esto podría significar que necesitamos GENERAR el rutKey")
print("   • O que el rutKey vacío ES la pista")

# ¿Y si la flag está en la secuencia de respuestas?
print("\n🔀 Análisis de secuencia...")
success_response = '{"rutKey":"","success":true}'
empty_rutkey = ""

# ¿Qué pasa si interpretamos el rutKey vacío como un placeholder?
print("   💡 rutKey vacío podría ser placeholder para:")
print("   • La flag misma")
print("   • Una clave que debemos descubrir")
print("   • Un valor derivado de nuestras credenciales")

# Técnica del CTF: a veces la flag está en lo que NO se muestra
print("\n🎭 Análisis inverso - ¿qué NO está ahí?")
print("   • El rutKey debería tener valor pero está vacío")
print("   • Success:true indica operación exitosa")
print("   • ¿Es el rutKey vacío intencionalmente la flag?")

# Generar posibles flags basados en las respuestas
possible_flags = [
    "CTF{rutKey_empty}",
    "CTF{vault_admin123}",
    "CTF{success_true}",
    "CTF{omnivault_core_api}",
    "CTF{empty_rutkey}",
    "flag{vault:admin123}",
    "FLAG{OMNIVAULT}",
    "CTF{vault_success}"
]

print(f"\n🎯 Posibles flags basadas en análisis:")
for possible in possible_flags:
    print(f"   • {possible}")

print("\n" + "=" * 55)
print("💡 CONSEJO DEL COORDINADOR: 'Analizar bien las respuestas'")
print("🔍 Las respuestas anteriores contienen la clave...")
print("=" * 55)