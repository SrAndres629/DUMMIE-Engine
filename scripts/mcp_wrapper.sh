#!/bin/bash
# DUMMIE Engine - MCP Error Wrapper (Hardened & Autocorrecting)
LOG_FILE="/tmp/dummie_mcp_errors.log"
export DUMMIE_ROOT_DIR="${DUMMIE_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
export DUMMIE_AIWG_DIR="${DUMMIE_AIWG_DIR:-$DUMMIE_ROOT_DIR/.aiwg}"
export MEMORY_SOCKET_PATH="${MEMORY_SOCKET_PATH:-$DUMMIE_AIWG_DIR/sockets/flight.sock}"

N8N_ENV_FILE_CANDIDATES=(
    "${DUMMIE_N8N_ENV_FILE:-}"
    "${N8N_ENV_FILE:-}"
    "${HOME}/Escritorio/n8n/.env"
    "${HOME}/Desktop/n8n/.env"
    "$(dirname "$DUMMIE_ROOT_DIR")/n8n/.env"
)

load_env_file() {
    local env_file=""
    for candidate in "${N8N_ENV_FILE_CANDIDATES[@]}"; do
        if [[ -n "$candidate" && -f "$candidate" ]]; then
            env_file="$candidate"
            break
        fi
    done

    if [[ -z "$env_file" ]]; then
        return 0
    fi

    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
    echo "[$(date)] Loaded env file: $env_file" >> "$LOG_FILE"
}


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

load_env_file

# La limpieza de caché npx es opt-in. Borrarla en cada arranque hace que el gateway
# dependa de red y estado global incluso cuando solo necesita abrir un pipe STDIO local.
if [[ "${DUMMIE_MCP_CLEAR_NPX_CACHE:-0}" == "1" ]]; then
    echo ">> [mcp_wrapper] Limpiando caché npx..." >> "$LOG_FILE"
    rm -rf ~/.npm/_npx/* 2>/dev/null || true
    rm -rf /media/datasets/CacheLinks/npm/_npx/* 2>/dev/null || true
else
    echo "[$(date)] Skipping npx cache cleanup. Set DUMMIE_MCP_CLEAR_NPX_CACHE=1 to enable." >> "$LOG_FILE"
fi

# Navegar al root de DUMMIE para que paths relativos funcionen
cd "$DUMMIE_ROOT_DIR" || {
    echo "[$(date)] CRITICAL: DUMMIE_ROOT_DIR='$DUMMIE_ROOT_DIR' no existe" >> "$LOG_FILE"
    exit 1
}

# Ejecutar con los argumentos corregidos
exec "${NEW_ARGS[@]}" 2>> "$LOG_FILE"
