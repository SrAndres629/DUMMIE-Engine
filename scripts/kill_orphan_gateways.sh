#!/bin/bash
# CANONICAL: Kills gateway processes NOT running under systemd supervision.
# Ran by ExecStartPost of dummie-gateway@.service after each gateway startup.
# This prevents orphan/zombie processes from manual runs (e.g. `uv run python -m gateway.* &`).
set -euo pipefail
KILLED=0
for pid in $(pgrep -f "gateway\.(media|code|infra|knowledge|shell)_gateway" 2>/dev/null || true); do
    if ! grep -q "\.service" "/proc/$pid/cgroup" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
        echo "[orphan-killer] Killed PID $pid (not under systemd)" >&2
        ((KILLED++))
    fi
done
[ "$KILLED" -gt 0 ] && echo "[orphan-killer] Cleaned $KILLED orphan gateway processes" >&2
exit 0
