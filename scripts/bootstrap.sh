#!/bin/bash
# DUMMIE Engine - Sovereign Bootstrap & Sensory Phase
# Based on ADR-006 & Spec 08

set -e

echo "=== [SENSORY PHASE] Detecting Environment Sovereignity ==="

# 1. Detect Nix
if command -v nix >/dev/null 2>&1; then
    echo "[✓] Nix detected. Active shell: $(if [[ -n "$IN_NIX_SHELL" ]]; then echo "Nix-Shell"; else echo "Native"; fi)"
    HAS_NIX=true
else
    echo "[!] Nix NOT detected on host."
    HAS_NIX=false
fi

# 2. Detect Docker
if command -v docker >/dev/null 2>&1; then
    DOCKER_VER=$(docker version --format '{{.Server.Version}}')
    echo "[✓] Docker detected: v$DOCKER_VER"
    HAS_DOCKER=true
else
    echo "[!] Docker NOT detected. Portability compromised."
    HAS_DOCKER=false
fi

# 3. Detect Local Runtimes
echo "--- Local Toolchain Audit (User-Space Priority) ---"

# Asegurar que ~/.local/bin esté en el PATH para el script
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"

check_tool() {
    local name=$1
    local cmd=$2
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "[$name] $cmd: $( "$cmd" version 2>&1 | head -n 1 || "$cmd" --version 2>&1 | head -n 1 )"
    else
        echo "[$name] $cmd: MISSING in PATH"
    fi
}

check_tool "L1" "go"
check_tool "L0" "elixir"
check_tool "L2" "uv"
check_tool "L3" "cargo"
check_tool "L4" "zig"

# 4. Determine Execution Path (ADR-006 & ADR-0014)
if [ "$HAS_NIX" = true ]; then
    EXEC_PATH="NIX_NATIVE"
    echo ">> Recommendation: Use 'nix develop' for all builds."
elif [ "$HAS_DOCKER" = true ]; then
    # Verificar si docker requiere sudo
    if docker ps >/dev/null 2>&1; then
        echo "[✓] Docker available WITHOUT sudo."
        EXEC_PATH="DOCKER_SOVEREIGN"
    else
        echo "[!] Docker detected but requires SUDO or group membership."
        echo "    Action: run 'sudo usermod -aG docker \$USER' and restart session."
        EXEC_PATH="DOCKER_RESTRICTED"
    fi
else
    EXEC_PATH="HOST_USER_SPACE"
    echo ">> Strategy: Falling back to User-Space tools (Zero-Sudo)."
fi

# 5. Export state to Session Context
cat <<EOF > governance/session_context.json
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": {
    "has_nix": $HAS_NIX,
    "has_docker": $HAS_DOCKER,
    "execution_path": "$EXEC_PATH",
    "user_space_ready": $(command -v uv >/dev/null 2>&1 && echo true || echo false)
  },
  "physical_truth": {
    "l0_overseer": "SKELETAL",
    "l1_nervous": "SKELETAL",
    "l2_brain": "EMPTY",
    "contracts": "CORE_UNIFIED"
  }
}
EOF

echo ">> Session context crystallized in governance/session_context.json"
