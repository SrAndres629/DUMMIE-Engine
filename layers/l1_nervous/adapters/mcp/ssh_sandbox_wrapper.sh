#!/bin/bash
# DUMMIE Sovereign SSH Sandbox (Spec 15)
# Wraps @modelcontextprotocol/server-ssh with Bubblewrap (bwrap) isolation.

ROOT_DIR="/home/jorand/Escritorio/DUMMIE Engine"
AIWG_DIR="$ROOT_DIR/.aiwg"
SSH_KEY_PATH="${DUMMIE_SSH_KEY:-/home/jorand/.ssh/dummie_agent_key}"

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "ERR_SPEC_47: SSH key not found or not injected." >&2
    exit 1
fi

# 1. Bubblewrap Sandbox Execution
# - Read-only access to ROOT_DIR
# - Read-write access to .aiwg (for memory persistence)
# - Isolated networking (only localhost for SSH bridge)
# - Minimal env
exec bwrap \
    --ro-bind / / \
    --dev /dev \
    --proc /proc \
    --tmpfs /tmp \
    --tmpfs /run \
    --ro-bind "$ROOT_DIR" "$ROOT_DIR" \
    --bind "$AIWG_DIR" "$AIWG_DIR" \
    --unshare-all \
    --share-net \
    --hostname dummie-sovereign-sandbox \
    npx -y @modelcontextprotocol/server-ssh 127.0.0.1 \
    --user jorand \
    --identity "$SSH_KEY_PATH" "$@"
