#!/bin/bash
set -e

# Configuración de Rutas
ROOT_DIR="/home/jorand/Escritorio/DUMMIE Engine"
BIN_DIR="$ROOT_DIR/bin"
L1_VENV="$ROOT_DIR/layers/l1_nervous/.venv/bin/python3"
SOCKET_PATH="/tmp/dummie_memory_audit.sock"
DB_PATH="/tmp/kuzu_audit_db"

echo "=== INICIANDO AUDITORÍA INDUSTRIAL DE EXTREMO A EXTREMO ==="

# 1. Limpieza de entorno
echo "[1/5] Limpiando sockets y DBs previas..."
rm -rf "$DB_PATH"
rm -f "$SOCKET_PATH"
mkdir -p "$BIN_DIR"

# 2. Build de componentes
echo "[2/5] Compilando Memory Plane y Overseer..."
cd "$ROOT_DIR/layers/l1_nervous" && go build -o "$BIN_DIR/memory_server" ./cmd/memory/main.go
cd "$ROOT_DIR/layers/l0_overseer" && go build -o "$BIN_DIR/overseer" ./cmd/overseer

# 3. Levantar Memory Plane en segundo plano
echo "[3/5] Levantando Memory Plane (Online Mode)..."
export KUZU_DB_PATH="$DB_PATH"
export MEMORY_SOCKET_PATH="$SOCKET_PATH"
"$BIN_DIR/memory_server" > /dev/null 2>&1 &
SERVER_PID=$!

# Esperar a que el socket esté listo
for i in {1..10}; do
    if [ -S "$SOCKET_PATH" ]; then
        echo "      Memory Plane activo en $SOCKET_PATH"
        break
    fi
    sleep 1
done

if [ ! -S "$SOCKET_PATH" ]; then
    echo "ERROR: Memory Plane no inició a tiempo."
    kill "$SERVER_PID" || true
    exit 1
fi

# Inicializar Tabla (Si es necesario, aunque verify_compression lo intenta)
MEMORY_SOCKET_PATH="$SOCKET_PATH" "$L1_VENV" -c "from layers.l1_nervous.memory_ipc import ArrowMemoryBridge; import os; bridge = ArrowMemoryBridge(os.getenv('MEMORY_SOCKET_PATH')); bridge.ipc.execute('CREATE NODE TABLE MemoryState(id STRING, causal_hash_v2 STRING, summary STRING, type STRING, timestamp INT64, msg_count INT64, PRIMARY KEY(id))')" || true
sleep 2

# 4. Ejecutar Suite de Verificación (MODO ONLINE)
echo "[4/5] Ejecutando Verificación de Compresión (ONLINE)..."
MEMORY_SOCKET_PATH="$SOCKET_PATH" "$L1_VENV" "$ROOT_DIR/scripts/verify_compression.py"

echo "[5/5] Ejecutando Verificación de Integridad de Prefijo (Go)..."
cd "$ROOT_DIR/layers/l0_overseer" && go test -v ./internal/orchestrator/...

# 5. Cleanup
echo "=== AUDITORÍA COMPLETADA CON ÉXITO ==="
kill "$SERVER_PID"
rm -rf "$DB_PATH"
rm -f "$SOCKET_PATH"
