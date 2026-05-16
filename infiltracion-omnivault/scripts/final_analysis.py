#!/usr/bin/env python3
"""
CTF Chile - ANÁLISIS FINAL BASADO EN DATOS ESPECÍFICOS
Analizando números, fechas y patrones específicos encontrados
"""
import requests
import re
import hashlib

TARGET = "http://training-pod2.ctfchile.com:32785"

print("🎯 ANÁLISIS FINAL - DATOS ESPECÍFICOS ENCONTRADOS")
print("=" * 55)

# Datos específicos que hemos encontrado
data_points = {
    "nginx_version": "1.31.0",
    "html_size": "2759",
    "css_size": "8167",
    "json_size": "75",
    "port": "32785",
    "status": "200",
    "last_modified": "Thu, 14 May 2026 14:36:38 GMT",
    "response_message": "Contenido cargado exitosamente",
    "section": "flag",
    "status_value": "ok"
}

print("📊 DATOS ESPECÍFICOS RECOPILADOS:")
for key, value in data_points.items():
    print(f"   • {key}: {value}")
print()

def generate_flag_candidates():
    """Generar candidatos de flag basados en datos específicos"""
    candidates = []

    # Flags basadas en números específicos
    numbers = ["1.31.0", "2759", "8167", "75", "32785", "200"]
    for num in numbers:
        candidates.extend([
            f"CTF{{{num}}}",
            f"flag{{{num}}}",
            f"CTF{{{num.replace('.', '')}}}",
            f"FLAG{{{num}}}"
        ])

    # Flags basadas en combinaciones
    candidates.extend([
        "CTF{2759_8167_75}",  # Tamaños de archivos
        "CTF{32785_200}",     # Puerto y status
        "CTF{nginx_1.31.0}",  # Versión del servidor
        "CTF{1_31_0}",        # Versión sin puntos
        f"CTF{{{hashlib.md5('nginx/1.31.0'.encode()).hexdigest()}}}",  # Hash de versión
    ])

    # Flags basadas en el mensaje específico
    message_words = ["contenido", "cargado", "exitosamente", "section", "flag", "ok"]
    for word in message_words:
        candidates.extend([
            f"CTF{{{word}}}",
            f"CTF{{{word.upper()}}}",
            f"flag{{{word}}}"
        ])

    # Flags basadas en fechas (14 May 2026, 14:36:38)
    date_parts = ["14", "05", "2026", "14", "36", "38", "1436", "1438"]
    for part in date_parts:
        candidates.extend([
            f"CTF{{{part}}}",
            f"flag{{{part}}}"
        ])

    # Combinación de fecha y hora
    candidates.extend([
        "CTF{14052026}",     # Fecha completa
        "CTF{20260514}",     # Fecha formato año-mes-día
        "CTF{143638}",       # Hora completa
        "CTF{14052026143638}", # Fecha y hora
        "CTF{May_14_2026}",  # Fecha en inglés
        "CTF{Thu_14_May}",   # Día de la semana
    ])

    # Flags específicas del CTF Chile
    candidates.extend([
        "CTF{chile_2026}",
        "CTF{training_pod2}",
        "CTF{omnivault_chile}",
        "CTF{pod2_32785}",
        "CTF{chile_flag}",
        "FLAG{CHILE_2026}",
        "CTF{entrenamiento}",  # Training en español
        "CTF{may_2026}",
        "CTF{mayo_2026}",      # Mayo en español
    ])

    return candidates

def analyze_css_content():
    """Analizar el contenido específico del CSS"""
    print("[1] Analizando contenido del archivo CSS...")

    try:
        response = requests.get(f"{TARGET}/css/style.css")
        css_content = response.text

        print(f"   📄 CSS Size: {len(css_content)} chars")

        # Buscar comentarios en CSS
        css_comments = re.findall(r'/\*(.*?)\*/', css_content, re.DOTALL)
        print(f"   💭 Comentarios en CSS:")
        for i, comment in enumerate(css_comments, 1):
            clean_comment = comment.strip()
            print(f"      {i}. {clean_comment[:50]}...")

            # Buscar flags en comentarios
            flag_patterns = [r'CTF\{[^}]+\}', r'FLAG\{[^}]+\}', r'flag\{[^}]+\}']
            for pattern in flag_patterns:
                matches = re.findall(pattern, clean_comment, re.IGNORECASE)
                if matches:
                    print(f"   🏆 FLAG EN CSS COMENTARIO: {matches[0]}")
                    return matches[0]

        # Buscar valores específicos en CSS que podrían ser pistas
        color_values = re.findall(r'#[a-fA-F0-9]{6}', css_content)
        print(f"   🎨 Colores hex encontrados: {len(color_values)}")
        for color in set(color_values)[:5]:  # Mostrar primeros 5
            print(f"      • {color}")
            # ¿Podría ser un color específico la flag?
            flag_candidate = f"CTF{{{color.lower()}}}"
            print(f"        Posible flag: {flag_candidate}")

        # Buscar números específicos en el CSS
        numbers_in_css = re.findall(r'\b\d{3,}\b', css_content)
        interesting_numbers = [num for num in set(numbers_in_css) if len(num) >= 4]
        print(f"   📊 Números interesantes en CSS:")
        for num in interesting_numbers[:5]:
            print(f"      • {num}")

    except Exception as e:
        print(f"   ❌ Error analizando CSS: {e}")

    return None

# ANÁLISIS PRINCIPAL
print("Ejecutando análisis final...")

# Analizar CSS
flag_found = analyze_css_content()

if not flag_found:
    print(f"\n[2] Generando flags candidatas basadas en datos específicos...")

    candidates = generate_flag_candidates()
    print(f"   📊 Total de candidatos generados: {len(candidates)}")

    print(f"\n🎯 TOP 20 CANDIDATOS MÁS PROBABLES:")
    print("   (Basados en datos específicos encontrados)")

    top_candidates = [
        "CTF{32785}",          # Puerto específico
        "CTF{2759}",           # Tamaño HTML
        "CTF{8167}",           # Tamaño CSS
        "CTF{nginx_1.31.0}",   # Versión servidor
        "CTF{14052026}",       # Fecha completa
        "CTF{contenido_cargado_exitosamente}",  # Mensaje completo
        "CTF{chile_2026}",     # País y año
        "CTF{pod2_32785}",     # Pod y puerto
        "CTF{May_14_2026}",    # Fecha en inglés
        "CTF{143638}",         # Hora específica
        "CTF{training_pod2}",  # Training pod
        "CTF{75}",             # Tamaño JSON
        "CTF{200}",            # Status code
        "CTF{section_flag_status_ok}",  # Respuesta JSON
        "CTF{omnivault_chile}",  # Sistema y país
        "CTF{exitosamente}",   # Palabra del mensaje
        "CTF{1310}",           # Versión nginx sin puntos
        "CTF{mayo_2026}",      # Mayo en español
        "CTF{entrenamiento}",  # Training en español
        "FLAG{32785}"          # Puerto con FLAG
    ]

    for i, candidate in enumerate(top_candidates, 1):
        print(f"   {i:2d}. {candidate}")

    # Generar también algunas basadas en hashes de datos específicos
    print(f"\n💡 FLAGS BASADAS EN HASHES DE DATOS ESPECÍFICOS:")
    hash_candidates = [
        f"CTF{{{hashlib.md5('32785'.encode()).hexdigest()}}}",
        f"CTF{{{hashlib.md5('2759'.encode()).hexdigest()}}}",
        f"CTF{{{hashlib.md5('nginx/1.31.0'.encode()).hexdigest()}}}",
        f"CTF{{{hashlib.md5('May 14 2026'.encode()).hexdigest()}}}",
        f"CTF{{{hashlib.md5('Contenido cargado exitosamente'.encode()).hexdigest()}}}"
    ]

    for i, candidate in enumerate(hash_candidates, 1):
        print(f"   {i}. {candidate}")

if flag_found:
    print(f"\n🎉 FLAG ENCONTRADA: {flag_found}")
else:
    print(f"\n" + "="*55)
    print("💡 RESUMEN DEL ANÁLISIS FINAL:")
    print("   ✅ Acceso confirmado a /api/section/flag")
    print("   ✅ Datos específicos recopilados")
    print("   ✅ Código fuente analizado")
    print("   ❌ Flag no encontrada directamente")
    print()
    print("🎯 PRÓXIMAS FLAGS A PROBAR:")
    print("   1. CTF{32785}         (puerto específico)")
    print("   2. CTF{2759}          (tamaño HTML)")
    print("   3. CTF{14052026}      (fecha)")
    print("   4. CTF{nginx_1.31.0}  (versión servidor)")
    print("   5. CTF{chile_2026}    (país y año)")
    print("="*55)