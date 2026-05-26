#!/bin/bash
# === CANONICAL ARCHITECTURE v2 ===
# Gateways are now managed by systemd (dummie-gateway@.service template).
# This script is a HEALTH CHECK tool, NOT a process launcher.
# Use: systemctl start dummie-engine  (orchestrator starts all 5 gateways)
# Use: systemctl status dummie-gateway@media  (per-gateway status)
set -euo pipefail

ROOT="${DUMMIE_ROOT:-/opt/dummie-engine}"
RUNTIME="$ROOT/.aiwg/runtime/gateways"

GATEWAYS=(media code infra knowledge shell)
HEALTHY=0

echo "=== MetaGateway Health Check ==="
echo "Root: $ROOT"
echo ""

for name in "${GATEWAYS[@]}"; do
    SVC="dummie-gateway@${name}.service"
    ACTIVE=$(systemctl is-active "$SVC" 2>/dev/null || echo "unknown")
    READY=$(cat "$RUNTIME/${name}.ready" 2>/dev/null || echo "not-ready")

    if [ "$ACTIVE" = "active" ] && [ "$READY" = "ready" ]; then
        echo "[✓] $name: systemd=$ACTIVE ready=$READY"
        ((HEALTHY++))
    else
        echo "[✗] $name: systemd=$ACTIVE ready=$READY"
    fi
done

echo ""
echo "=== ${HEALTHY}/${#GATEWAYS[@]} gateways healthy ==="
[ "$HEALTHY" -eq "${#GATEWAYS[@]}" ] && exit 0 || exit 1
