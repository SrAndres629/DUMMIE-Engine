#!/usr/bin/env bash
# DUMMIE Doctor Repair Orchestrator (Industrial Proxy)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPAIR_PY="$ROOT_DIR/scripts/dummie_repair.py"

echo "=== [DUMMIE DOCTOR] Invocando Protocolo de Auto-Curación Industrial ==="
cd "$ROOT_DIR" && uv run python "$REPAIR_PY"
