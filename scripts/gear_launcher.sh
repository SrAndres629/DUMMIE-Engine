#!/bin/bash

# DUMMIE Engine - Hardware-Aware Gear Launcher
# Following ADR-0016 (Industrial Gear Integration)

MIN_FREE_RAM_MB=2048
REGISTRY_FILE="./shared/gear_registry.json"

function check_resources() {
    local free_ram=$(free -m | awk '/^Mem:/{print $4}')
    if [ "$free_ram" -lt "$MIN_FREE_RAM_MB" ]; then
        echo "[❌] ERROR: Insufficient hardware capacity ($free_ram MB < $MIN_FREE_RAM_MB MB)."
        echo "[!] Circuit Breaker triggered (ADR-0016). Aborting launch."
        exit 1
    fi
}

function launch_gear() {
    local gear_id=$1
    echo "[⚙️] Initializing Gear: $gear_id..."
    
    # Check if gear exists in registry
    local gear_info=$(grep -A 10 "\"id\": \"$gear_id\"" "$REGISTRY_FILE")
    if [ -z "$gear_info" ]; then
        echo "[❌] ERROR: Gear '$gear_id' not found in registry."
        exit 1
    fi

    check_resources

    case $gear_id in
        "aider")
            # Aider is a CLI gear
            exec aider "$@"
            ;;
        "code-bundler-pro")
            # Code Bundler Pro logic
            echo "[📦] Bundling context..."
            # Placeholder for actual command
            ;;
        *)
            echo "[⚠️] Gear '$gear_id' integrated via MCP. Use the configured MCP server."
            ;;
    esac
}

if [ -z "$1" ]; then
    echo "Usage: $0 <gear_id> [args]"
    exit 1
fi

launch_gear "$@"
