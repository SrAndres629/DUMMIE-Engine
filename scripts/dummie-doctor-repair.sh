#!/usr/bin/env bash
set -euo pipefail

# DUMMIE Doctor Repair Orchestrator
# Goal: Scan, Heal, Cycle, Verify.

ROOT_DIR="/home/jorand/Escritorio/DUMMIE Engine"
VENV_PYTHON="$ROOT_DIR/layers/l2_brain/.venv/bin/python3"
DOCTOR_PY="$ROOT_DIR/scripts/dummie_mcp_doctor.py"
STATE_DIR="$ROOT_DIR/state"
mkdir -p "$STATE_DIR"

PRE_LOG="$STATE_DIR/doctor_pre.json"
POST_LOG="$STATE_DIR/doctor_post.json"
REPAIR_REPORT="$STATE_DIR/repair_audit.md"

echo "=== [1/5] DIAGNOSTIC PHASE ==="
# We run the doctor and extract the JSON part
"$VENV_PYTHON" "$DOCTOR_PY" --json --skip-codex > "$STATE_DIR/doctor_pre_raw.log" 2>&1 || true
sed -n '/--- JSON START ---/,/--- JSON END ---/p' "$STATE_DIR/doctor_pre_raw.log" | sed '1d;$d' > "$PRE_LOG"

echo "=== [2/5] HEALING PHASE ==="
# 1. Kill redundant mcp_server.py processes
# We look for processes that are not the current one and have mcp_server.py
# The doctor already captured them in .results.processes.relevant
RELEVANT_PIDS=$(jq -r '.results.processes.relevant[] | split(" ")[0]' "$PRE_LOG" || echo "")

if [[ -n "$RELEVANT_PIDS" ]]; then
    echo "Found potentially orphan MCP processes: $RELEVANT_PIDS"
    for pid in $RELEVANT_PIDS; do
        if ps -p "$pid" > /dev/null; then
            echo "Killing orphan PID $pid..."
            kill -TERM "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
        fi
    done
fi

# 2. Clear legacy sockets
find "$ROOT_DIR/.aiwg/sockets/" -name "*.sock" -type s -atime +1 -delete 2>/dev/null || true

# 3. Memory flush (Safe caches)
echo "Attempting to flush filesystem caches..."
sudo sync && echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null || echo "Could not flush caches (skip)."

echo "=== [3/5] SUBSTRATE CYCLE ==="
echo "Stopping lab..."
/usr/local/bin/dummie-lab-off

echo "Starting lab..."
/usr/local/bin/dummie-lab-on

echo "=== [4/5] VERIFICATION PHASE ==="
sleep 5 # Wait for services to settle
"$VENV_PYTHON" "$DOCTOR_PY" --json --skip-codex > "$STATE_DIR/doctor_post_raw.log" 2>&1 || true
sed -n '/--- JSON START ---/,/--- JSON END ---/p' "$STATE_DIR/doctor_post_raw.log" | sed '1d;$d' > "$POST_LOG"

echo "=== [5/5] AUDIT REPORT ==="
{
    echo "# DUMMIE Repair Audit Report"
    echo "Timestamp: $(date)"
    echo ""
    echo "## Summary"
    PRE_OK=$(jq -r '.ok' "$PRE_LOG")
    POST_OK=$(jq -r '.ok' "$POST_LOG")
    echo "- Pre-repair State: **$PRE_OK**"
    echo "- Post-repair State: **$POST_OK**"
    echo ""
    echo "## Resource Delta"
    PRE_RAM=$(jq -r '.results.system_resources.ram.used' "$PRE_LOG")
    POST_RAM=$(jq -r '.results.system_resources.ram.used' "$POST_LOG")
    echo "- RAM Used: ${PRE_RAM}MB -> ${POST_RAM}MB"
    
    echo ""
    echo "## Process Cleanup"
    if [[ -n "$RELEVANT_PIDS" ]]; then
        echo "Killed PIDs: $RELEVANT_PIDS"
    else
        echo "No orphan processes found."
    fi
    
    echo ""
    echo "## Handshake Verification"
    HANDSHAKE_OK=$(jq -r '.results.mcp_handshake_ok' "$POST_LOG")
    if [[ "$HANDSHAKE_OK" == "true" ]]; then
        echo "- Handshake: **SUCCESS**"
    else
        ERROR=$(jq -r '.results.mcp_handshake_error // "Unknown error"' "$POST_LOG")
        echo "- Handshake: **FAIL** ($ERROR)"
    fi
    
    echo ""
    echo "## Substrate Status"
    echo "- Gateway Config: $(jq -r '.results.gateway_config_ok' "$POST_LOG")"
    echo "- Runtime Sockets: $(jq -r '.results.runtime_sockets_ok' "$POST_LOG")"
} > "$REPAIR_REPORT"

echo "Repair complete. See $REPAIR_REPORT for details."
cat "$REPAIR_REPORT"
