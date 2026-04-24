#!/bin/bash
# DUMMIE Engine - MCP Error Wrapper
# Captura el stderr de los servidores MCP para que el agente pueda diagnosticar fallos.

LOG_FILE="/tmp/dummie_mcp_errors.log"

# Asegurar que el archivo de log existe y es escribible
touch "$LOG_FILE"
echo "--- SESSION START: $(date) ---" >> "$LOG_FILE"

# Ejecutar el comando original y capturar stderr
# Usamos exec para que el proceso hijo herede el PID y las señales
exec "$@" 2>> "$LOG_FILE"
