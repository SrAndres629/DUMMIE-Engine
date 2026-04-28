#!/bin/bash
set -e

# Configuración de Rutas
ROOT_DIR="${DUMMIE_ROOT:-$(pwd)}"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
DB_PATH="$AIWG_DIR/memory/loci.db"
SOCKET_PATH="$AIWG_DIR/sockets/flight.sock"
BIN_DIR="$ROOT_DIR/bin"
LOG_FILE="$ROOT_DIR/layers/l1_nervous/memory_server_sovereign.log"

echo "=== [DUMMIE ENGINE] Inicializando Sovereign Memory Daemon ==="

# 1. Asegurar directorios
mkdir -p "$AIWG_DIR/memory"
mkdir -p "$AIWG_DIR/sockets"

# 2. Purgar procesos zombies y conexiones muertas
echo "[*] Purgando procesos zombies de memory_server..."
pkill -f "memory_server" || true
sleep 1

# 3. Limpieza de Lock Files huérfanos (La causa del modo degradado)
if [ -d "$DB_PATH" ]; then
    LOCK_FILES=$(find "$DB_PATH" -name "*.lock" 2>/dev/null)
    if [ -n "$LOCK_FILES" ]; then
        echo "[!] Detectados archivos de bloqueo huérfanos. Ejecutando purga quirúrgica..."
        rm -f "$DB_PATH"/*.lock
        echo "[✓] Bloqueos liberados."
    fi
fi

# 4. Iniciar el Daemon en background
echo "[*] Levantando Sovereign Memory Daemon (Arrow Flight)..."
DUMMIE_KUZU_DB_PATH="$DB_PATH" MEMORY_SOCKET_PATH="$SOCKET_PATH" nohup "$BIN_DIR/memory_server" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 5. Verificación de Handshake
echo "[*] Esperando inicialización del socket IPC..."
for i in {1..10}; do
    if [ -S "$SOCKET_PATH" ]; then
        echo "[✓] Sovereign Memory Daemon ACTIVO en: $SOCKET_PATH"
        echo "[✓] PID: $SERVER_PID"
        exit 0
    fi
    sleep 1
done

echo "[X] ERROR CRÍTICO: El Memory Daemon no pudo inicializarse. Revisa $LOG_FILE"
kill "$SERVER_PID" || true
exit 1
