#!/bin/bash
# DUMMIE Engine — Canonical Upgrade Script
# Run: sudo ./scripts/upgrade.sh
set -euo pipefail

ROOT="${DUMMIE_ROOT:-/opt/dummie-engine}"
AIWG="$ROOT/.aiwg"
VERSION_FILE="$AIWG/state/version.json"

echo "=== DUMMIE Engine Upgrade ==="

CURRENT="unknown"
if [ -f "$VERSION_FILE" ]; then
    CURRENT=$(python3 -c "import json; print(json.load(open('$VERSION_FILE')).get('version','unknown'))")
    echo "Current version: $CURRENT"
else
    echo "No previous version found — treating as fresh install"
    CURRENT="0.0.0"
fi

cd "$ROOT"

# Migrations
if [ "$CURRENT" = "0.0.0" ] || [ "$CURRENT" = "0.1.0" ]; then
    echo "[migrate] v0.x → v2.0.0: updating models_config.json if needed..."
    # Already done in this session
fi

# Git pull (if on main branch)
if git rev-parse --is-inside-work-tree &>/dev/null; then
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" = "main" ]; then
        echo "[git] Pulling latest..."
        git pull --ff-only origin main || echo "  WARNING: git pull failed — continuing with current code"
    fi
fi

# Update venv
echo "[venv] Updating dependencies..."
uv sync

# Install/update systemd units
echo "[systemd] Updating units..."
bash "$ROOT/scripts/install.sh"

# Restart services using auto-discovery
echo "[systemd] Restarting DUMMIE services..."

if command -v dummie-lab-discover &>/dev/null; then
    echo "  Using auto-discovery for restart order..."
    DISCOVERY=$(dummie-lab-discover)
    START_ORDER=$(echo "$DISCOVERY" | python3 -c "import sys,json; [print(s) for s in json.load(sys.stdin)['start_order']]")

    # Restart in dependency order
    while IFS= read -r svc; do
        SVC_LEVEL=$(echo "$DISCOVERY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data['services']:
    if s['name'] == '$svc':
        print(s['level'])
        break
" 2>/dev/null || echo "system")

        if [ "$SVC_LEVEL" = "user" ]; then
            systemctl --user restart "$svc.service" 2>/dev/null && echo "    $svc (user) restarted" || echo "    $svc (user) restart failed"
        else
            systemctl restart "$svc.service" 2>/dev/null && echo "    $svc restarted" || echo "    $svc restart failed (may be masked/disabled)"
        fi
    done <<< "$START_ORDER"
else
    echo "  [WARN] dummie-lab-discover not found, using fallback restart order..."
    systemctl restart dummie-memory dummie-engine
    sleep 5
    systemctl restart dummie-opencode dummie-session
    systemctl restart dummie-gateway@media dummie-gateway@code dummie-gateway@infra dummie-gateway@knowledge dummie-gateway@shell 2>/dev/null || true
fi

echo ""
echo "=== Upgrade complete ==="
echo "Check: sudo journalctl -fu 'dummie-*'"
