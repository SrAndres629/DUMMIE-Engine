#!/bin/bash
# DUMMIE Engine - MCP Error Wrapper (Hardened & Autocorrecting)
LOG_FILE="/tmp/dummie_mcp_errors.log"
export MEMORY_SOCKET_PATH="${MEMORY_SOCKET_PATH:-/tmp/dummie_flight.sock}"
export DUMMIE_ROOT_DIR="${DUMMIE_ROOT_DIR:-/home/jorand/Escritorio/DUMMIE Engine}"
export DUMMIE_AIWG_DIR="${DUMMIE_AIWG_DIR:-/home/jorand/Escritorio/DUMMIE Engine/.aiwg}"

# Autocorregir argumentos obsoletos
NEW_ARGS=()
for arg in "$@"; do
    if [[ "$arg" == *"adapters/mcp/server.py" ]]; then
        NEW_ARGS+=("${arg/adapters\/mcp\/server.py/mcp_server.py}")
    else
        NEW_ARGS+=("$arg")
    fi
done

touch "$LOG_FILE"
echo "--- SESSION ATTEMPT: $(date) ---" >> "$LOG_FILE"
echo "[$(date)] Original Args: $@" >> "$LOG_FILE"
echo "[$(date)] Corrected Args: ${NEW_ARGS[@]}" >> "$LOG_FILE"

# Ejecutar con los argumentos corregidos
exec "${NEW_ARGS[@]}" 2>> "$LOG_FILE"
