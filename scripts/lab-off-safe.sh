#!/usr/bin/env bash
# DUMMIE Engine - Safe Lab Shutdown
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHUTDOWN_SCRIPT="$ROOT_DIR/scripts/shutdown_factory.sh"

echo "=== [SAFE-OFF] Stopping DUMMIE Application Stack ==="

if [ -f "$SHUTDOWN_SCRIPT" ]; then
    bash "$SHUTDOWN_SCRIPT"
else
    echo "Warning: $SHUTDOWN_SCRIPT not found. Falling back to pkill."
    pkill -f "DUMMIE Engine" || true
fi

# Stop ollama if wanted (Optional, usually safe to keep on)
# sudo systemctl stop ollama || true

echo "DUMMIE lab is OFFLINE."
