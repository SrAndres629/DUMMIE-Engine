#!/bin/bash
set -e

ROOT="${DUMMIE_ROOT:-/media/datasets/DUMMIE Engine}"
SYSD_DIR="$ROOT/scripts/systemd"
SERVICES=(
    "dummie-memory.service"
    "dummie-engine.service"
    "dummie-guardian.service"
)

echo "=== DUMMIE Engine — Systemd Service Installer ==="
echo "Root: $ROOT"
echo ""

# Validate all service files exist
for svc in "${SERVICES[@]}"; do
    if [ ! -f "$SYSD_DIR/$svc" ]; then
        echo "[✗] Missing: $SYSD_DIR/$svc"
        exit 1
    fi
done
echo "[✓] All 3 service files present"
echo ""

# Stop running services first
echo "[*] Stopping running services..."
for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        systemctl stop "$svc"
        echo "  - $svc stopped"
    fi
done

# Install service files
echo "[*] Installing service files..."
for svc in "${SERVICES[@]}"; do
    cp "$SYSD_DIR/$svc" "/etc/systemd/system/$svc"
    chmod 644 "/etc/systemd/system/$svc"
    echo "  - $svc installed"
done

# Reload systemd
systemctl daemon-reload
echo "[✓] systemd reloaded"

# Enable all services
for svc in "${SERVICES[@]}"; do
    systemctl enable "$svc"
    echo "  - $svc enabled"
done

# Start in dependency order
echo ""
echo "[*] Starting services (memory → engine → guardian)..."
systemctl start dummie-memory.service
echo "  - dummie-memory.service started"

# Wait for memory socket
for i in $(seq 1 10); do
    if [ -S "/media/datasets/DUMMIE Engine/.aiwg/sockets/flight.sock" ]; then
        echo "  - Memory socket ready"
        break
    fi
    sleep 1
done

systemctl start dummie-engine.service
echo "  - dummie-engine.service started"

systemctl start dummie-guardian.service
echo "  - dummie-guardian.service started"

# Verify all services
echo ""
echo "=== Status ==="
for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        echo "[✓] $svc — ACTIVE"
    else
        echo "[✗] $svc — NOT ACTIVE"
        systemctl status "$svc" --no-pager 2>&1 | tail -5
        FAILED=1
    fi
done

echo ""
if [ -z "$FAILED" ]; then
    echo "[✓] All services installed and running"
else
    echo "[!] Some services failed — check 'journalctl -u <service>'"
    exit 1
fi
