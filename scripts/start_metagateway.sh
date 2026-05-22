#!/bin/bash
set -e

ROOT="${DUMMIE_ROOT:-/media/datasets/DUMMIE Engine}"
L1="$ROOT/layers/l1_nervous"
RUNTIME="$ROOT/.aiwg/runtime/gateways"
BIN="${L1}/dummie_nervous"

mkdir -p "$RUNTIME"

echo "=== MetaGateway Launcher ==="
echo "Root: $ROOT"

# Kill existing sub-gateways
echo "[*] Purging existing sub-gateway processes..."
pkill -f "gateway/(media|code|infra|knowledge|shell)_gateway.py" 2>/dev/null || true
sleep 1

# Clean up old readiness files
rm -f "$RUNTIME"/*.ready "$RUNTIME"/*.pid

# Start each sub-gateway in background
declare -A GATEWAYS=(
    ["media"]=8081
    ["code"]=8082
    ["infra"]=8083
    ["knowledge"]=8084
    ["shell"]=8085
)

FAILED=0
for name in "${!GATEWAYS[@]}"; do
    port="${GATEWAYS[$name]}"
    echo "[*] Starting ${name} gateway on port ${port}..."
    cd "$L1"
    uv run python "gateway/${name}_gateway.py" &
    PID=$!
    echo $PID > "$RUNTIME/${name}.pid"
    echo "[+] ${name} gateway PID: $PID"
done

# Verify readiness
echo ""
echo "[*] Verifying sub-gateway readiness..."
for i in $(seq 1 10); do
    READY_COUNT=0
    for name in "${!GATEWAYS[@]}"; do
        if [ -f "$RUNTIME/${name}.ready" ]; then
            ((READY_COUNT++))
        fi
    done
    if [ "$READY_COUNT" -eq "${#GATEWAYS[@]}" ]; then
        echo "[✓] All ${#GATEWAYS[@]} sub-gateways ready"
        exit 0
    fi
    sleep 1
done

echo "[✗] Not all sub-gateways ready after 10s"
for name in "${!GATEWAYS[@]}"; do
    if [ ! -f "$RUNTIME/${name}.ready" ]; then
        echo "  - ${name} NOT ready"
        ((FAILED++))
    fi
done
exit $FAILED
