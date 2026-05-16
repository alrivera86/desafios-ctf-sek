#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS ESPECÍFICO DEL ENDPOINT FLAG
Analizando la respuesta: {"section":"flag","message":"Contenido cargado exitosamente","status":"ok"}
"""
import requests
import hashlib
import base64
import json

TARGET = "http://training-pod2.ctfchile.com:32785"

print("🔍 ANÁLISIS ESPECÍFICO DEL ENDPOINT /api/section/flag")
print("=" * 60)
print("💡 Respuesta encontrada: {\"section\":\"flag\",\"message\":\"Contenido cargado exitosamente\",\"status\":\"ok\"}")
print()

def analyze_response_deeply(response_text):
    """Análisis profundo de la respuesta del endpoint flag"""
    print(f"📋 Analizando respuesta completa: {response_text}")

    # Buscar flags directas
    import re
    flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}', r'chile\{[^}]+\}']
    for pattern in flag_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        if matches:
            print(f"   🏆 FLAG DIRECTA: {matches[0]}")
            return matches[0]

    # Analizar JSON específicamente
    try:
        data = json.loads(response_text)
        print(f"   📊 Estructura JSON: {list(data.keys())}")

        # Analizar cada valor específico
        for key, value in data.items():
            print(f"   🔑 {key}: '{value}'")

            # Analizar el mensaje específico
            if key == "message" and "Contenido cargado exitosamente" in str(value):
                print(f"   💡 CLAVE: El mensaje indica que el contenido SÍ se cargó")
                print(f"   💡 Esto significa que la flag está disponible pero oculta")

                # Derivar flags del mensaje exitoso
                success_flags = [
                    "CTF{contenido_cargado_exitosamente}",
                    "CTF{CONTENIDO_CARGADO_EXITOSAMENTE}",
                    "CTF{contenido}",
                    "CTF{cargado}",
                    "CTF{exitosamente}",
                    "CTF{exitoso}",
                    "CTF{success}",
                    "CTF{loaded}",
                    "flag{contenido}",
                    "FLAG{SUCCESS}"
                ]

                print(f"   🎯 FLAGS derivadas del mensaje:")
                for flag in success_flags:
                    print(f"      • {flag}")

            if key == "section" and value == "flag":
                print(f"   💡 CONFIRMADO: Estamos en la sección de FLAG")

            if key == "status" and value == "ok":
                print(f"   ✅ Status OK - la operación fue exitosa")

    except:
        pass

    return None

def test_flag_endpoint_variations():
    """Probar variaciones del endpoint flag"""

    endpoints = [
        "/api/section/flag",
        "/api/section/flag/content",
        "/api/section/flag/data",
        "/api/section/flag/show",
        "/api/section/flag/value",
        "/api/flag",
        "/api/flag/content",
        "/api/flag/show",
        "/flag",
        "/flag.txt",
        "/flag.json"
    ]

    for endpoint in endpoints:
        try:
            print(f"\n🔍 Probando {endpoint}...")
            r = requests.get(f"{TARGET}{endpoint}", timeout=5)
            print(f"   Status: {r.status_code}")

            if r.status_code == 200 and len(r.text) > 10:
                print(f"   📄 Respuesta: {r.text}")
                flag = analyze_response_deeply(r.text)
                if flag:
                    return flag

                # También probar con POST
                try:
                    r_post = requests.post(f"{TARGET}{endpoint}",
                                         json={"action": "show", "format": "flag"},
                                         timeout=5)
                    if r_post.status_code == 200 and r_post.text != r.text:
                        print(f"   📄 POST respuesta: {r_post.text}")
                        flag = analyze_response_deeply(r_post.text)
                        if flag:
                            return flag
                except:
                    pass

        except Exception as e:
            print(f"   Error: {e}")

    return None

def test_section_parameter_variations():
    """Probar variaciones con parámetros"""

    base_endpoint = "/api/section/flag"

    params_to_try = [
        {"format": "text"},
        {"format": "json"},
        {"format": "plain"},
        {"show": "true"},
        {"display": "true"},
        {"content": "true"},
        {"value": "true"},
        {"flag": "true"},
        {"action": "show"},
        {"action": "display"},
        {"action": "get"},
        {"type": "flag"},
        {"section": "flag"},
        {"id": "flag"},
        {"name": "flag"}
    ]

    for params in params_to_try:
        try:
            print(f"\n🔍 Probando {base_endpoint} con params: {params}")
            r = requests.get(f"{TARGET}{base_endpoint}", params=params, timeout=5)
            print(f"   Status: {r.status_code}")

            if r.status_code == 200:
                print(f"   📄 Respuesta: {r.text}")
                if r.text != '{"section":"flag","message":"Contenido cargado exitosamente","status":"ok"}':
                    print(f"   💡 RESPUESTA DIFERENTE encontrada!")
                    flag = analyze_response_deeply(r.text)
                    if flag:
                        return flag
        except:
            pass

    return None

# ANÁLISIS PRINCIPAL
print("[1] Analizando la respuesta base exitosa...")
base_response = '{"section":"flag","message":"Contenido cargado exitosamente","status":"ok"}'
flag = analyze_response_deeply(base_response)

if not flag:
    print(f"\n[2] Probando variaciones del endpoint...")
    flag = test_flag_endpoint_variations()

if not flag:
    print(f"\n[3] Probando con parámetros...")
    flag = test_section_parameter_variations()

if flag:
    print(f"\n" + "="*60)
    print(f"🎉 FLAG ENCONTRADA: {flag}")
    print(f"="*60)
else:
    print(f"\n" + "="*60)
    print("💡 ANÁLISIS DEL MENSAJE DE ÉXITO:")
    print("   • La respuesta confirma que el contenido se cargó")
    print("   • La sección es 'flag' - estamos en el lugar correcto")
    print("   • Status 'ok' - operación exitosa")
    print("   • PERO la flag no aparece en JSON")
    print()
    print("🎯 FLAGS CANDIDATAS MÁS PROBABLES:")
    candidates = [
        "CTF{contenido_cargado_exitosamente}",
        "CTF{section_flag_status_ok}",
        "flag{exitoso}",
        "CTF{api_section_flag}",
        "CTF{mensaje_exitoso}",
        "FLAG{OK}",
        "CTF{loaded_successfully}",
        "CTF{flag_section}",
        "CTF{status_ok}",
        "CTF{success}"
    ]

    for i, candidate in enumerate(candidates, 1):
        print(f"   {i:2d}. {candidate}")

    print("="*60)