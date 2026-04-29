#!/bin/bash
# DUMMIE Engine - Shutdown Factory Script

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"
LEGACY_DUMMIED_SOCKET_PATH="$AIWG_DIR/dummied.sock"
FLIGHT_SOCKET_PATH="${MEMORY_SOCKET_PATH:-$AIWG_DIR/sockets/flight.sock}"

echo "=== [SHUTDOWN] Cerrando DUMMIE Engine Factory ==="

# 1. Matar procesos por nombre/patrón
echo "[*] Terminando procesos principales e hijos (Orphan Reaper)..."
pkill -f "dummied"
pkill -f "mix run --no-halt"
pkill -f "monitor"
pkill -f "l1_nervous"
pkill -f "mcp_server.py"
pkill -f "go run cmd/memory/main.go"
pkill -f "mcp-server-sqlite"
pkill -f "mcp-ripgrep"
pkill -f "mcp-ctags"
pkill -f "genkit-cli"
pkill -f "arize-tracing-assistant"
pkill -f "mcp-server-fetch"
pkill -f "mcp-server-time"
pkill -f "mcp_server_ssh"
pkill -f "server-puppeteer"
pkill -f "server-everything"

# 2. Limpieza de Sockets
echo "[*] Limpiando sockets Unix..."
rm -f /tmp/dummied.sock
rm -f "$LEGACY_DUMMIED_SOCKET_PATH"
rm -f "$DUMMIED_SOCKET_PATH"
rm -f /tmp/dummie_flight.sock
rm -f "$FLIGHT_SOCKET_PATH"

# 3. Limpieza de PID files (opcional)
rm -f l1.pid l0.pid

echo "[✓] Todos los procesos terminados y sockets liberados."
