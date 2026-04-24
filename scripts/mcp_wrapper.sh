#!/bin/bash
# DUMMIE Engine - MCP Error Wrapper (Hardened)
# Captura el stderr de los servidores MCP y realiza validaciones pre-flight.

LOG_FILE="/tmp/dummie_mcp_errors.log"

# Asegurar que el archivo de log existe y es escribible
touch "$LOG_FILE"
echo "--- SESSION ATTEMPT: $(date) ---" >> "$LOG_FILE"

# Pre-flight check: Verificar que el ejecutable existe
EXECUTABLE="$1"

if [[ -z "$EXECUTABLE" ]]; then
    echo "[$(date)] ERROR: No executable provided to wrapper." >> "$LOG_FILE"
    exit 1
fi

# Intentar localizar el ejecutable si no es un path absoluto
if ! command -v "$EXECUTABLE" >/dev/null 2>&1 && [ ! -f "$EXECUTABLE" ]; then
    echo "[$(date)] CRITICAL: Executable not found or not in PATH: $EXECUTABLE" >> "$LOG_FILE"
    echo "Current PATH: $PATH" >> "$LOG_FILE"
    exit 1
fi

# Log the command being executed
echo "[$(date)] Executing: $@" >> "$LOG_FILE"

# Ejecutar el comando original y capturar stderr
# Usamos exec para que el proceso hijo herede el PID y las señales
exec "$@" 2>> "$LOG_FILE"
