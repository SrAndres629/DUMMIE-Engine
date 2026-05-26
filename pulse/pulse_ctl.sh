#!/bin/bash
# pulse_ctl.sh — DUMMIE Pulse Engine control script
# Source of Truth: /opt/dummie-engine/.aiwg/pulse/
# Traced: pulse/run_pulse.py
set -euo pipefail

RUNDIR="/opt/dummie-engine/.aiwg/pulse"
LOGDIR="/opt/dummie-engine/.aiwg/reports"
PIDFILE="$RUNDIR/pulse.pid"
LOGFILE="$LOGDIR/pulse.log"
PYTHON="/usr/bin/python3"
RUNNER="/opt/dummie-engine/pulse/run_pulse.py"

mkdir -p "$RUNDIR" "$LOGDIR"

running() {
    [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null
}

start() {
    if running; then
        echo "Pulse Engine already running (PID $(cat "$PIDFILE"))"
        return 0
    fi
    echo "Starting DUMMIE Pulse Engine..."
    nohup "$PYTHON" "$RUNNER" start >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    sleep 1
    if running; then
        echo "Pulse Engine started (PID $(cat "$PIDFILE"))"
    else
        echo "ERROR: Pulse Engine failed to start — check $LOGFILE"
        rm -f "$PIDFILE"
        return 1
    fi
}

stop() {
    if ! running; then
        echo "Pulse Engine not running"
        rm -f "$PIDFILE"
        return 0
    fi
    local pid
    pid=$(cat "$PIDFILE")
    echo "Stopping Pulse Engine (PID $pid)..."
    kill "$pid" 2>/dev/null || true
    for i in $(seq 1 10); do
        kill -0 "$pid" 2>/dev/null || { echo "Stopped"; rm -f "$PIDFILE"; return 0; }
        sleep 0.5
    done
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "Force stopped"
}

status() {
    if running; then
        echo "Pulse Engine: RUNNING (PID $(cat "$PIDFILE"))"
        "$PYTHON" "$RUNNER" status
    else
        echo "Pulse Engine: STOPPED"
    fi
}

health() {
    "$PYTHON" "$RUNNER" health
}

logs() {
    if [ -f "$LOGFILE" ]; then
        tail "${1:-50}" "$LOGFILE"
    else
        echo "No log file at $LOGFILE"
    fi
}

guards() {
    "$PYTHON" "$RUNNER" status | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['guards'],indent=2))"
}

metrics() {
    "$PYTHON" "$RUNNER" health | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['metrics'],indent=2))"

}

trigger() {
    echo "Triggering manual pulse..."
    "$PYTHON" "$RUNNER" trigger
}

case "${1:-status}" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 1; start ;;
    status)  status ;;
    health)  health ;;
    logs)    logs "${2:-}" ;;
    guards)  guards ;;
    metrics) metrics ;;
    trigger) trigger ;;
    *) echo "Usage: $0 {start|stop|restart|status|health|trigger|logs|guards|metrics}"
       exit 1 ;;
esac
