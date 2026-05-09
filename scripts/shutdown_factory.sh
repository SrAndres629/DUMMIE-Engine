#!/bin/bash
# DUMMIE Engine - Shutdown Factory Script

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"
LEGACY_DUMMIED_SOCKET_PATH="$AIWG_DIR/dummied.sock"
FLIGHT_SOCKET_PATH="${MEMORY_SOCKET_PATH:-$AIWG_DIR/sockets/flight.sock}"

echo "=== [SHUTDOWN] Cerrando DUMMIE Engine Factory ==="

# 1. Matar procesos por nombre/patrón (Industrial Grade Reaper)
echo "[*] Terminando procesos de todas las capas (L0-L2)..."

# Patrones específicos de DUMMIE Engine
patterns=(
    "dummied"
    "mix run --no-halt"
    "monitor"
    "l1_nervous"
    "l0_overseer"
    "mcp_server.py"
    "mcp_proxy.py"
    "go run cmd/memory/main.go"
    "mcp-server-sqlite"
    "mcp-ripgrep"
    "mcp-ctags"
    "genkit-cli"
    "arize-tracing-assistant"
    "mcp-server-fetch"
    "mcp-server-time"
    "mcp_server_ssh"
    "server-puppeteer"
    "server-everything"
    "openclaw-gateway"
    "cloudcode_cli duet"
    "pyrefly lsp"
    "language_server.*DUMMIE_20Engine"
)

for pattern in "${patterns[@]}"; do
    # Intentar SIGTERM primero, luego SIGKILL si persiste
    pids=$(pgrep -f "$pattern" || true)
    if [ -n "$pids" ]; then
        echo "  [-] Killing $pattern (PIDs: $pids)..."
        kill -15 $pids 2>/dev/null || true
        sleep 0.5
        kill -9 $pids 2>/dev/null || true
    fi
done

# 2. Limpieza de Sockets Unix
echo "[*] Limpiando sockets Unix y archivos temporales..."
find /tmp -name "dummied.sock" -delete 2>/dev/null || true
find /tmp -name "dummie_flight.sock" -delete 2>/dev/null || true
find /tmp -name "server_*" -mmin -60 -delete 2>/dev/null || true # Limpiar pipes de language server recientes

rm -f "$LEGACY_DUMMIED_SOCKET_PATH"
rm -f "$DUMMIED_SOCKET_PATH"
rm -f "$FLIGHT_SOCKET_PATH"
rm -f "$AIWG_DIR/sockets/"*

# 3. Limpieza de PID files y estados de ejecución
rm -f l1.pid l0.pid monitor.pid
rm -f "$AIWG_DIR/runtime/lock" 2>/dev/null || true

echo "[✓] Todos los procesos terminados y recursos liberados."
