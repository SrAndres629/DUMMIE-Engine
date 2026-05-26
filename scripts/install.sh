#!/bin/bash
# DUMMIE Engine — Canonical Install Script (idempotent)
# Run: sudo ./scripts/install.sh
# Can be re-run safely: detects existing install, skips what's already done.
set -euo pipefail

ROOT="${DUMMIE_ROOT:-/opt/dummie-engine}"
SCRIPTS="$ROOT/scripts"
SYSTEMD="$SCRIPTS/systemd"
AIWG="$ROOT/.aiwg"
VERSION_FILE="$AIWG/state/version.json"

echo "=== DUMMIE Engine v2.0.0 — Canonical Install ==="
echo "Root: $ROOT"

# 1. Ensure root directory
if [ ! -d "$ROOT" ]; then
    echo "ERROR: DUMMIE_ROOT=$ROOT does not exist. Clone the repo first."
    exit 1
fi

# 2. Python venv
echo "[1/6] Setting up Python environment..."
cd "$ROOT"
if [ ! -d ".venv" ]; then
    uv sync
    echo "  .venv created"
else
    uv sync
    echo "  .venv updated"
fi

# 3. Install systemd units (idempotent — cp overrides existing)
echo "[2/6] Installing systemd units..."

SRV_FILES=(
    dummie-memory.service
    dummie-engine.service
    dummie-guardian.service
    dummie-opencode.service
    dummie-session.service
    dummie-models-pull.service
    dummie-gateway@.service
    agentic.slice
    agentic-workload.slice
)

TIMER_FILES=(
    dummie-models-pull.timer
)

for f in "${SRV_FILES[@]}"; do
    if [ -f "$SYSTEMD/$f" ]; then
        cp -f "$SYSTEMD/$f" /etc/systemd/system/
        echo "  $f"
    else
        echo "  SKIP $f (not found)"
    fi
done

for f in "${TIMER_FILES[@]}"; do
    if [ -f "$SYSTEMD/$f" ]; then
        cp -f "$SYSTEMD/$f" /etc/systemd/system/
        echo "  $f"
    fi
done

# 4. Reload systemd
echo "[3/6] Reloading systemd..."
systemctl daemon-reload

# 5. Enable services + timer (enable is idempotent)
echo "[4/6] Enabling services..."

ENABLE_SERVICES=(
    dummie-memory.service
    dummie-engine.service
    dummie-opencode.service
    dummie-session.service
)

for svc in "${ENABLE_SERVICES[@]}"; do
    if systemctl is-enabled "$svc" &>/dev/null; then
        echo "  $svc (already enabled)"
    else
        systemctl enable "$svc"
        echo "  $svc (enabled)"
    fi
done

# Timer
if systemctl is-enabled dummie-models-pull.timer &>/dev/null; then
    echo "  dummie-models-pull.timer (already enabled)"
else
    systemctl enable dummie-models-pull.timer
    echo "  dummie-models-pull.timer (enabled)"
fi

# 6. Write version file
echo "[5/6] Writing version state..."
mkdir -p "$AIWG/state"
cat > "$VERSION_FILE" <<EOF
{
  "version": "2.0.0",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "root": "$ROOT"
}
EOF
echo "  $VERSION_FILE"

# 7. Install lab management scripts
echo "[6/7] Installing lab management scripts..."

LAB_SCRIPTS=(
    dummie-lab-discover
    dummie-lab-on
    dummie-lab-off
    dummie-lab-status
)

for script in "${LAB_SCRIPTS[@]}"; do
    if [ -f "$SCRIPTS/$script" ]; then
        install -m 0755 "$SCRIPTS/$script" /usr/local/bin/
        echo "  $script"
    else
        echo "  SKIP $script (not found in repo)"
    fi
done

# 8. Done
echo "[7/7] Done."
echo ""
echo "  Start:   sudo systemctl start dummie-memory dummie-engine dummie-opencode dummie-session"
echo "  Status:  sudo systemctl status 'dummie-*'"
echo "  Logs:    sudo journalctl -fu 'dummie-*'"
echo "  Timer:   sudo systemctl start dummie-models-pull.timer"
