#!/bin/bash
# DUMMIE Engine - Full Factory Launcher (Hardened)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
SOCKET_PATH="${MEMORY_SOCKET_PATH:-$AIWG_DIR/sockets/flight.sock}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"
LEGACY_DUMMIED_SOCKET_PATH="$AIWG_DIR/dummied.sock"
# [HARDENING] Path canónico alineado con SOVEREIGN-4D
KUZU_PATH="${DUMMIE_KUZU_DB_PATH:-$AIWG_DIR/memory/loci.db}"

echo "=== [FACTORY] Iniciando DUMMIE Engine (Nivel 5) ==="

# 1. Higiene (No destructiva)
mkdir -p "$AIWG_DIR/sockets"
mkdir -p "$(dirname "$KUZU_PATH")"

rm -f "$SOCKET_PATH"
rm -f "$DUMMIED_SOCKET_PATH"
rm -f "$LEGACY_DUMMIED_SOCKET_PATH"

# 2. Iniciar L1 Nervous (Relojero)
echo ">> Launching L1 Nervous (Lamport)..."
cd "$ROOT_DIR/layers/l1_nervous" && go run main.go sidecar.go > "$ROOT_DIR/l1.log" 2>&1 &

# 3. Iniciar Memory Plane (Data Plane)
echo ">> Launching Memory Plane (Flight/Kuzu)..."
(cd "$ROOT_DIR/layers/l1_nervous" && DUMMIE_KUZU_DB_PATH="$KUZU_PATH" KUZU_DB_PATH="$KUZU_PATH" MEMORY_SOCKET_PATH="$SOCKET_PATH" go run cmd/memory/main.go) > "$ROOT_DIR/memory.log" 2>&1 &

# 4. Iniciar L0 Overseer (Daemon Go)
echo ">> Launching L0 Overseer (Daemon Go)..."
cd "$ROOT_DIR/layers/l0_overseer" && DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" DUMMIE_DUMMIED_SOCKET_PATH="$DUMMIED_SOCKET_PATH" go run cmd/dummied/main.go > "$ROOT_DIR/l0_go.log" 2>&1 &

# 5. Iniciar L0 Overseer (Supervisor Elixir)
echo ">> Launching L0 Overseer (Supervisor Elixir)..."
cd "$ROOT_DIR/layers/l0_overseer" && DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" mix run --no-halt > "$ROOT_DIR/l0_elixir.log" 2>&1 &

# 5. Iniciar L0 Monitor
echo ">> Launching L0 Monitor..."
cd "$ROOT_DIR/layers/l0_overseer" && DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" go run cmd/monitor/main.go > "$ROOT_DIR/monitor.log" 2>&1 &

# 6. Iniciar MCP Gateway (L1)
echo ">> Launching L1 MCP Gateway (Brain)..."
cd "$ROOT_DIR"
DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" DUMMIE_KUZU_DB_PATH="$KUZU_PATH" DUMMIE_DUMMIED_SOCKET_PATH="$DUMMIED_SOCKET_PATH" DUMMIE_MCP_CONFIG_PATH="$ROOT_DIR/dummie_gateway_config.json" MEMORY_SOCKET_PATH="$SOCKET_PATH" "./layers/l2_brain/.venv/bin/python" "./layers/l1_nervous/mcp_server.py" > mcp.log 2>&1 &

echo "[✓] Factory is ONLINE."
echo "Sockets: $DUMMIED_SOCKET_PATH, $SOCKET_PATH"
echo "Kuzu: $KUZU_PATH"
