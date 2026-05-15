#!/bin/bash
# DUMMIE Engine - Shutdown Factory Script

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"
LEGACY_DUMMIED_SOCKET_PATH="$AIWG_DIR/dummied.sock"
FLIGHT_SOCKET_PATH="${MEMORY_SOCKET_PATH:-$AIWG_DIR/sockets/flight.sock}"

echo "=== [SHUTDOWN] Cerrando DUMMIE Engine Factory ==="

# 1. Terminación Elegante vía Systemd y PID
echo "[*] Deteniendo servicio dummie-engine de Systemd..."
systemctl --user stop dummie-engine.service 2>/dev/null || true

SUPERVISOR_PID_FILE="$AIWG_DIR/supervisor.pid"
if [ -f "$SUPERVISOR_PID_FILE" ]; then
    SUPERVISOR_PID=$(cat "$SUPERVISOR_PID_FILE")
    if kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
        echo "[*] Enviando SIGTERM al L0 Supervisor (PID: $SUPERVISOR_PID)..."
        kill -15 "$SUPERVISOR_PID"
        
        # Esperar hasta 10 segundos para apagado ordenado
        for i in {1..10}; do
            if ! kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
                echo "  [✓] L0 Supervisor y sub-procesos terminaron correctamente."
                break
            fi
            sleep 1
        done
        
        if kill -0 "$SUPERVISOR_PID" 2>/dev/null; then
            echo "  [!] El Supervisor no respondió al SIGTERM. Forzando SIGKILL..."
            kill -9 "$SUPERVISOR_PID"
        fi
    fi
    rm -f "$SUPERVISOR_PID_FILE"
else
    echo "  [-] No se encontró supervisor.pid. (Omitiendo apagado primario)"
fi

# Fallback ultra-seguro solo para procesos zombis conocidos de dummie
for z_pattern in "l1_nervous/mcp_server.py" "l0_overseer/supervisor.py" "bin/dummied"; do
    pids=$(pgrep -f "$z_pattern" | grep -v "$$" || true)
    if [ -n "$pids" ]; then
        echo "  [-] Limpiando proceso zombi: $z_pattern"
        kill -9 $pids 2>/dev/null || true
    fi
done

# 2. Limpieza de Sockets Unix
echo "[*] Limpiando sockets Unix y archivos temporales..."
find /tmp -name "dummied.sock" -delete 2>/dev/null || true
find /tmp -name "dummie_flight.sock" -delete 2>/dev/null || true
find /tmp -name "server_*" -mmin -60 -delete 2>/dev/null || true # Limpiar pipes de language server recientes

rm -f "$LEGACY_DUMMIED_SOCKET_PATH"
rm -f "$DUMMIED_SOCKET_PATH"
rm -f "$FLIGHT_SOCKET_PATH"
rm -f "$AIWG_DIR/sockets/"*

# 3. Limpieza de PID files y estados de ejecución
rm -f l1.pid l0.pid monitor.pid
rm -f "$AIWG_DIR/runtime/lock" 2>/dev/null || true

echo "[✓] Todos los procesos terminados y recursos liberados."
