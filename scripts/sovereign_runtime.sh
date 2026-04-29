#!/bin/bash
# DUMMIE Engine - Sovereign Runtime Supervisor
# Manages the full lifecycle of the factory.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"

echo "=== [SOVEREIGN] Launching DUMMIE Engine Factory ==="

# 1. Hygiene check
"$ROOT_DIR/scripts/log_manager.sh"

# 2. Launch Nervous System (L1)
echo ">> Launching L1 Nervous..."
DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" DUMMIE_DUMMIED_SOCKET_PATH="$DUMMIED_SOCKET_PATH" "$ROOT_DIR/bin/l1_nervous" > "$ROOT_DIR/l1.log" 2>&1 &
L1_PID=$!

# 3. Launch Overseer (L0) - The Arbiter
echo ">> Launching L0 Overseer (Self-Healing Elixir)..."
(cd "$ROOT_DIR/layers/l0_overseer" && DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" mix run --no-halt) > "$ROOT_DIR/l0_elixir.log" 2>&1 &
L0_ELIXIR_PID=$!

echo ">> Launching L0 Overseer (Daemon Go)..."
(cd "$ROOT_DIR/layers/l0_overseer" && DUMMIE_ROOT_DIR="$ROOT_DIR" DUMMIE_AIWG_DIR="$AIWG_DIR" DUMMIE_DUMMIED_SOCKET_PATH="$DUMMIED_SOCKET_PATH" go run cmd/dummied/main.go) > "$ROOT_DIR/l0_go.log" 2>&1 &
L0_GO_PID=$!

echo ">> Factory is ONLINE. Monitoring PIDs: L1=$L1_PID, L0_GO=$L0_GO_PID, L0_ELIXIR=$L0_ELIXIR_PID"

# 4. Background log manager (every 5 minutes)
while true; do
    sleep 300
    "$ROOT_DIR/scripts/log_manager.sh"
done
