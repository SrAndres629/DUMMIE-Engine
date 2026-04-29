#!/bin/bash
# DUMMIE Engine - Sovereign Runtime Supervisor
# Manages the full lifecycle of the factory.

set -e

echo "=== [SOVEREIGN] Launching DUMMIE Engine Factory ==="

# 1. Hygiene check
./scripts/log_manager.sh

# 2. Launch Nervous System (L1)
echo ">> Launching L1 Nervous..."
./bin/l1_nervous > l1.log 2>&1 &
L1_PID=$!

# 3. Launch Overseer (L0) - The Arbiter
echo ">> Launching L0 Overseer (Self-Healing Elixir)..."
cd layers/l0_overseer && mix run --no-halt > ../../l0_elixir.log 2>&1 &
L0_ELIXIR_PID=$!

echo ">> Launching L0 Overseer (Daemon Go)..."
cd layers/l0_overseer && go run cmd/dummied/main.go > ../../l0_go.log 2>&1 &
L0_GO_PID=$!
cd ../..

echo ">> Factory is ONLINE. Monitoring PIDs: L1=$L1_PID, L0=$L0_PID"

# 4. Background log manager (every 5 minutes)
while true; do
    sleep 300
    ./scripts/log_manager.sh
done
