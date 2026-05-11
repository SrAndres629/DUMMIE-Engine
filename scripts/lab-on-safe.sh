#!/usr/bin/env bash
# DUMMIE Engine - Safe Lab Startup
set -euo pipefail

ROOT_DIR="/home/jorand/Escritorio/DUMMIE Engine"
START_SCRIPT="$ROOT_DIR/scripts/factory_up.sh"

echo "=== [SAFE-ON] Launching DUMMIE Application Stack ==="

if [ ! -f "$START_SCRIPT" ]; then
    echo "Error: $START_SCRIPT not found. Cannot start lab."
    exit 1
fi

# Ensure Ollama is running (non-destructive)
if systemctl list-unit-files | grep -q "ollama"; then
    sudo systemctl start ollama || true
fi

# Run the local factory launcher
bash "$START_SCRIPT"

echo "DUMMIE lab is ONLINE."
