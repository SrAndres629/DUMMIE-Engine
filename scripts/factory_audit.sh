#!/bin/bash
# DUMMIE Engine - Industrial Factory Audit
# This script verifies the 'Physical Truth' of the factory.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== [AUDIT] Starting Industrial Factory Verification ===${NC}"

# 1. Herramientas
echo -n ">> Checking Toolchain: "
if command -v go >/dev/null && command -v zig >/dev/null && command -v rustc >/dev/null && command -v elixir >/dev/null && command -v uv >/dev/null; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Missing tools${NC}"
    exit 1
fi

# 2. Infraestructura
echo -n ">> Checking NATS Heartbeat: "
if pgrep nats-server >/dev/null; then
    echo -e "${GREEN}[OK] (Running)${NC}"
else
    echo -e "${RED}[FAIL] NATS is dead${NC}"
    exit 1
fi

# 3. Capas Core (Binarios)
echo -n ">> Checking L1 Nervous (Go): "
if [ -f "bin/l1_nervous" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Binary missing${NC}"
fi

echo -n ">> Checking L4 Edge (Zig): "
if [ -f "layers/l4_edge/zig-out/bin/lst_scanner" ] || [ -f "layers/l4_edge/zig-out/bin/l4_edge" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Zig binary missing${NC}"
fi

# 4. Capas L2 (Python)
echo -n ">> Checking L2 Brain (Python): "
if [ -d "layers/l2_brain/.venv" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Virtualenv missing${NC}"
fi

# 5. Capas L3 (Rust)
echo -n ">> Checking L3 Shield (Rust): "
if [ -d "layers/l3_shield/target/release" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Release build missing${NC}"
fi

# 6. Capa L0 (Elixir)
echo -n ">> Checking L0 Overseer (Elixir): "
if [ -d "layers/l0_overseer/_build/dev/lib/overseer" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAIL] Compilation missing${NC}"
fi

echo -e "${BLUE}--- AUDIT COMPLETE ---${NC}"
