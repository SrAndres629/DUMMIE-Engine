#!/bin/bash
# DUMMIE MCP Bridge Wrapper - Final Stability Fix
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# SCRIPT_DIR is /.../DUMMIE Engine/layers/l1_nervous/adapters/mcp
# We need to go up 3 levels to reach PROJECT_ROOT
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/layers/l2_brain/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Syncing L2 Brain environment at $PROJECT_ROOT/layers/l2_brain..."
    cd "$PROJECT_ROOT/layers/l2_brain" && uv sync
fi

echo "Launching DUMMIE MCP Server from $SCRIPT_DIR..."
export DUMMIE_SSH_KEY="/home/jorand/.ssh/dummie_agent_key"
cd "$SCRIPT_DIR"
exec "$VENV_PYTHON" server.py "$@"
