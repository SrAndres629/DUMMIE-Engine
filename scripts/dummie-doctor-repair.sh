#!/usr/bin/env bash
# DUMMIE Doctor Repair Orchestrator (Industrial Proxy)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$ROOT_DIR/layers/l2_brain/.venv/bin/python3"
REPAIR_PY="$ROOT_DIR/scripts/dummie_repair.py"

echo "=== [DUMMIE DOCTOR] Invocando Protocolo de Auto-Curación Industrial ==="
"$VENV_PYTHON" "$REPAIR_PY"
