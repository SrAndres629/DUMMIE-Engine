#!/usr/bin/env bash
# DUMMIE Engine - Hardware Provisioning (Optional)
# This script manages ASUS-specific hardware services.
# Run ONLY when you need to change power/GPU profiles.

set -euo pipefail

echo "=== [HARDWARE] Provisioning ASUS Substrate ==="

# Check if services exist
if systemctl list-unit-files | grep -q "asusd"; then
    echo ">> Managing asusd..."
    sudo systemctl start asusd || true
fi

if systemctl list-unit-files | grep -q "supergfxd"; then
    echo ">> Managing supergfxd (GPU Mode)..."
    echo "WARNING: This may restart your graphical session if a mode switch occurs."
    sudo systemctl start supergfxd || true
fi

if systemctl list-unit-files | grep -q "zram-config"; then
    echo ">> Managing zram..."
    sudo systemctl start zram-config || true
fi

echo "[✓] Hardware substrate is configured."
