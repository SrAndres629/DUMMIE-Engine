#!/bin/bash
set -e

# Configuración de Rutas
ROOT_DIR="${DUMMIE_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
export DUMMIE_ROOT="$ROOT_DIR"
export DUMMIE_AIWG="/tmp/dummie_audit_aiwg"
BIN_DIR="$ROOT_DIR/bin"
L1_VENV="$ROOT_DIR/layers/l1_nervous/.venv/bin/python3"

# Rutas derivadas
SOCKET_PATH="$DUMMIE_AIWG/sockets/flight.sock"
DB_PATH="$DUMMIE_AIWG/memory/loci.db"
SERVER_PID=""

cleanup() {
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
        kill "$SERVER_PID" || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    rm -rf "$DUMMIE_AIWG"
}

trap cleanup EXIT
echo "=== INICIANDO AUDITORÍA INDUSTRIAL DE EXTREMO A EXTREMO ==="

# 1. Limpieza de entorno
echo "[1/5] Limpiando entorno de auditoría..."
rm -rf "$DUMMIE_AIWG"
mkdir -p "$BIN_DIR"
mkdir -p "$DUMMIE_AIWG/memory"
mkdir -p "$DUMMIE_AIWG/sockets"

# 2. Build de componentes
echo "[2/5] Compilando Memory Plane y Overseer (All Commands)..."
cd "$ROOT_DIR/layers/l1_nervous" && go build -o "$BIN_DIR/memory_server" ./cmd/memory/main.go
cd "$ROOT_DIR/layers/l0_overseer" && go build -o "$BIN_DIR/" ./cmd/...

# 3. Levantar Memory Plane en segundo plano
echo "[3/5] Levantando Memory Plane (Online Mode)..."
DUMMIE_KUZU_DB_PATH="$DB_PATH" MEMORY_SOCKET_PATH="$SOCKET_PATH" "$BIN_DIR/memory_server" > /dev/null 2>&1 &
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


# 4. Ejecutar Suite de Verificación (MODO ONLINE)
echo "[4/6] Ejecutando Verificación de Compresión (ONLINE)..."
MEMORY_SOCKET_PATH="$SOCKET_PATH" "$L1_VENV" "$ROOT_DIR/scripts/verify_compression.py"

echo "[5/6] Ejecutando Auditoría de Contratos y Merkle-DAG (Python)..."
# Usamos el venv de L2 para los tests de modelos
cd "$ROOT_DIR/layers/l2_brain" && uv run pytest tests/test_contract_drift.py tests/test_causal_integrity.py

echo "[6/6] Ejecutando Verificación de Integridad de Prefijo (Go)..."
cd "$ROOT_DIR/layers/l0_overseer" && go test -v ./internal/orchestrator/...

# 5. Cleanup
echo "=== AUDITORÍA COMPLETADA CON ÉXITO ==="
cleanup
trap - EXIT
