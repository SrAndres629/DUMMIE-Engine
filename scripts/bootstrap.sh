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
echo "--- Local Toolchain Audit ---"
command -v go >/dev/null 2>&1 && echo "[L1] Go: $(go version)" || echo "[L1] Go: MISSING"
command -v elixir >/dev/null 2>&1 && echo "[L0] Elixir: $(elixir --version | grep Elixir)" || echo "[L0] Elixir: MISSING"
command -v uv >/dev/null 2>&1 && echo "[L2] uv (Python): $(uv --version)" || echo "[L2] uv: MISSING"

# 4. Determine Execution Path (ADR-006)
if [ "$HAS_NIX" = true ]; then
    EXEC_PATH="NIX_NATIVE"
    echo ">> Recommendation: Use 'nix develop' for all builds."
elif [ "$HAS_DOCKER" = true ]; then
    EXEC_PATH="DOCKER_SOVEREIGN"
    echo ">> Recommendation: Use 'Dockerfile.builder' for L0, L1, L3, L4 builds."
else
    EXEC_PATH="HOST_CONTAMINATED"
    echo ">> WARNING: Host lacks hermeticity. Manual tool installation required (NOT RECOMMENDED)."
fi

# 5. Export state to Session Context
cat <<EOF > governance/session_context.json
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": {
    "has_nix": $HAS_NIX,
    "has_docker": $HAS_DOCKER,
    "execution_path": "$EXEC_PATH"
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
