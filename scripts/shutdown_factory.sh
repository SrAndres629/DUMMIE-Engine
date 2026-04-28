#!/bin/bash
# DUMMIE Engine - Shutdown Factory Script

echo "=== [SHUTDOWN] Cerrando DUMMIE Engine Factory ==="

# 1. Matar procesos por nombre/patrón
echo "[*] Terminando procesos principales e hijos (Orphan Reaper)..."
pkill -f "dummied"
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
rm -f /tmp/dummie_flight.sock
rm -f /home/jorand/Escritorio/DUMMIE\ Engine/.aiwg/sockets/flight.sock

# 3. Limpieza de PID files (opcional)
rm -f l1.pid l0.pid

echo "[✓] Todos los procesos terminados y sockets liberados."
