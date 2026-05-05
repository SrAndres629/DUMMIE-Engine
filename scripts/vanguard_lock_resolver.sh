#!/bin/bash
# scripts/vanguard_lock_resolver.sh
# DUMMIE Engine - 2026 Process Lifecycle Management

# Usamos rutas absolutas para evitar ambigüedades
ROOT_DIR="${DUMMIE_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MEMORY_DIR="$ROOT_DIR/.aiwg/memory"

echo "=== [VANGUARD] Auditoría de bloqueos en $MEMORY_DIR ==="

# 1. Identificar procesos que tienen archivos abiertos en el directorio de memoria
# lsof devuelve los PIDs de los procesos que tienen descriptores de archivos abiertos
LOCKING_PIDS=$(lsof -t "$MEMORY_DIR" 2>/dev/null)

if [ -z "$LOCKING_PIDS" ]; then
    echo "[✓] No se detectaron bloqueos activos en el directorio de memoria."
else
    echo "[!] Detectados procesos bloqueantes potenciales: $LOCKING_PIDS"
    for PID in $LOCKING_PIDS; do
        # Obtener comando y argumentos del proceso
        CMD=$(ps -p $PID -o comm= 2>/dev/null)
        ARGS=$(ps -p $PID -o args= 2>/dev/null)
        
        echo "[*] Evaluando PID $PID ($CMD)..."
        
        # Solo matamos procesos que parezcan ser del Engine (Python/MCP)
        if echo "$ARGS" | grep -qE "python|mcp_server|verify_spec30|brain"; then
            echo "[!] Ejecutando terminación forzada de $PID..."
            kill -15 $PID 2>/dev/null
            sleep 0.5
            kill -9 $PID 2>/dev/null
            echo "[✓] PID $PID eliminado."
        else
            echo "[i] Proceso $PID no parece ser un objetivo del Engine. Se mantiene vivo."
        fi
    done
fi

# 2. Limpieza de procesos por coincidencia de nombre (pgrep) para capturar huérfanos sin archivos abiertos
echo "=== [VANGUARD] Escaneo de procesos huérfanos por patrón ==="
ORPHAN_PIDS=$(pgrep -f "mcp_server.py|verify_spec30|brain.mcp_server")

if [ -n "$ORPHAN_PIDS" ]; then
    echo "[!] Detectados procesos huérfanos: $ORPHAN_PIDS"
    echo "$ORPHAN_PIDS" | xargs kill -9 2>/dev/null
    echo "[✓] Procesos huérfanos eliminados."
else
    echo "[✓] No se encontraron procesos huérfanos adicionales."
fi

# 3. Limpiar sockets previos
echo "=== [VANGUARD] Limpieza de sockets IPC ==="
rm -f /tmp/dummie_memory.sock
rm -f /tmp/dummie_memory_test.sock

echo "[✓] Entorno listo para SPEC-30."
