#!/usr/bin/env python3
"""
CTF Chile - EXTRACCIÓN DE FLAGS DEL WEBHOOK EXITOSO
"""
import requests
import base64
import re

WEBHOOK_UUID = "300bbadc-4b48-4608-bbf0-1c2b19d4f909"

print("🏆 EXTRAYENDO FLAGS DEL WEBHOOK EXITOSO")
print("=" * 50)

try:
    r = requests.get(f"https://webhook.site/token/{WEBHOOK_UUID}/requests?per_page=200", timeout=15)
    if r.status_code == 200:
        data = r.json().get("data", [])
        print(f"📊 {len(data)} requests analizando...")

        flags_found = []
        ssh_successes = []

        for req in data:
            url = req.get("url", "")
            content = req.get("content", "") + " " + req.get("text_content", "")

            # Extraer tag del path
            path_parts = url.split("/")
            tag = path_parts[-1] if path_parts else "unknown"

            if content:
                # Buscar flags
                flag_patterns = [
                    r'CTF\{[^}]+\}',
                    r'FLAG\{[^}]+\}',
                    r'flag\{[^}]+\}',
                    r'chile\{[^}]+\}'
                ]

                for pattern in flag_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        flags_found.append({
                            "source": tag,
                            "flag": match
                        })

                # Buscar éxitos SSH
                if "SUCCESS_SSH" in content:
                    ssh_successes.append({
                        "source": tag,
                        "content": content[:300]
                    })

                # Decodificar base64 si existe
                base64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)
                for b64 in base64_patterns:
                    try:
                        decoded = base64.b64decode(b64).decode('utf-8', 'ignore')
                        if 'CTF{' in decoded or 'FLAG{' in decoded or 'flag{' in decoded:
                            flags_found.append({
                                "source": f"{tag}_decoded",
                                "flag": decoded
                            })
                    except:
                        pass

        print(f"\n🏆 FLAGS ENCONTRADAS: {len(flags_found)}")
        for i, flag_info in enumerate(flags_found):
            print(f"   {i+1}. {flag_info['flag']} (fuente: {flag_info['source']})")

        print(f"\n✅ ÉXITOS SSH: {len(ssh_successes)}")
        for success in ssh_successes:
            print(f"   • {success['source']}: {success['content'][:100]}...")

        if not flags_found:
            print("\n🔍 CONTENIDO RELEVANTE:")
            # Mostrar contenido relevante sin flags
            relevant_content = []
            for req in data:
                content = req.get("content", "") + " " + req.get("text_content", "")
                if content and len(content.strip()) > 20 and "error" not in content.lower():
                    url = req.get("url", "")
                    tag = url.split("/")[-1] if "/" in url else "unknown"
                    relevant_content.append({
                        "source": tag,
                        "content": content[:200]
                    })

            for item in relevant_content[:10]:  # Mostrar primeros 10
                print(f"   • {item['source']}: {item['content']}...")

    else:
        print(f"❌ Error accediendo webhook: {r.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🔗 Webhook completo: https://webhook.site/#!/{WEBHOOK_UUID}")
print("="*50)