#!/bin/bash
# pulse_ctl.sh — Pulse Engine control script
# Systemd: dummie-pulse.service
# Port: 8090

set -e

SERVICE="dummie-pulse.service"
HEALTH_URL="http://localhost:8090/health"

case "$1" in
    start)
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE"
        sudo systemctl start "$SERVICE"
        echo "Pulse Engine started"
        sleep 2
        curl -sf "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "(health check pending)"
        ;;
    stop)
        sudo systemctl stop "$SERVICE"
        sudo systemctl disable "$SERVICE"
        echo "Pulse Engine stopped"
        ;;
    restart)
        sudo systemctl restart "$SERVICE"
        echo "Pulse Engine restarted"
        ;;
    status)
        systemctl status "$SERVICE" --no-pager
        echo "---"
        curl -sf "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "(health check unavailable)"
        ;;
    trigger)
        curl -sf -X POST "http://localhost:8090/trigger" && echo ""
        ;;
    health)
        curl -sf "$HEALTH_URL" | python3 -m json.tool
        ;;
    logs)
        journalctl -u "$SERVICE" -f
        ;;
    guards)
        curl -sf "$HEALTH_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['guards'], indent=2))"
        ;;
    metrics)
        curl -sf "$HEALTH_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['metrics'], indent=2))"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|trigger|health|logs|guards|metrics}"
        exit 1
        ;;
esac
