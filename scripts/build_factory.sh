#!/usr/bin/env bash
# DUMMIE Engine - Industrial Build System
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$ROOT_DIR/bin"

echo "=== [BUILD] Compiling DUMMIE Industrial Binaries ==="
mkdir -p "$BIN_DIR"

# 1. L1 Nervous (Sidecar)
echo ">> Building L1 Nervous Sidecar..."
cd "$ROOT_DIR/layers/l1_nervous"
go build -o "$BIN_DIR/l1_sidecar" main.go sidecar.go

# 2. Memory Plane
echo ">> Building Memory Plane (Flight/Kuzu)..."
cd "$ROOT_DIR/layers/l1_nervous"
go build -o "$BIN_DIR/memory_plane" cmd/memory/main.go

# 3. L0 Overseer (Daemon)
echo ">> Building L0 Overseer (dummied)..."
cd "$ROOT_DIR/layers/l0_overseer"
go build -o "$BIN_DIR/dummied" cmd/dummied/main.go

# 4. L0 Monitor
echo ">> Building L0 Monitor..."
cd "$ROOT_DIR/layers/l0_overseer"
go build -o "$BIN_DIR/monitor" cmd/monitor/main.go

# 5. L1 Tools (Ingester/Diag)
echo ">> Building L1 Utility Tools..."
cd "$ROOT_DIR/layers/l1_nervous"
go build -o "$BIN_DIR/mcp_ingester" cmd/ingester/main.go
go build -o "$BIN_DIR/mcp_diag" cmd/diag_kuzu/main.go

echo "=== [BUILD] SUCCESS: Binaries available in $BIN_DIR ==="
ls -lh "$BIN_DIR"
