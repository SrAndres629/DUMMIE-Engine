#!/bin/bash
# 🛡️ DUMMIE ENGINE: SECURITY TOGGLE
# Uso: ./toggle_security.sh [high|low]

MODE=$(echo "$1" | tr '[:upper:]' '[:lower:]')

if [[ "$MODE" == "high" ]]; then
    echo "[🛡️] Activando Modo SOBERANO (Sandbox bwrap: loopback activado)."
    export DUMMIE_SANDBOX_MODE="ON"
    # Persistir para la sesión actual del shell si se hace source
    # O instruir al usuario a reiniciar el servicio.
elif [[ "$MODE" == "low" ]]; then
    echo "[🔓] Activando Modo PROXIMIDAD (Sandbox desactivado - Ejecución directa)."
    export DUMMIE_SANDBOX_MODE="OFF"
else
    echo "Uso: $0 [high|low]"
    echo "  high: Máxima seguridad cuando no estás presente."
    echo "  low:  Ejecución directa (más rápido, menos restricciones)."
    exit 1
fi

# Guardar estado en un archivo para que el mcp_server lo lea
echo "$DUMMIE_SANDBOX_MODE" > "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/security_state"

echo "[✓] Estado de seguridad actualizado a: $DUMMIE_SANDBOX_MODE"
echo "[!] Nota: Los servidores MCP ya activos deben reiniciarse para aplicar el cambio."
