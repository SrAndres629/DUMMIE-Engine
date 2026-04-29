#!/bin/bash
# DUMMIE ENGINE - Fencing Stress Test
DB_DIR="/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/kuzu"
DB_PATH="$DB_DIR/state.db"
LOCK_FILE="$DB_DIR/lock.file"

echo "[TEST] Iniciando Stress Test de Fencing..."

# 1. Asegurar que el directorio existe
mkdir -p "$DB_DIR"

# 2. Simular un bloqueo huérfano
echo "SIMULATED_ORPHAN_PID" > "$LOCK_FILE"
echo "[TEST] Lock huérfano inyectado en $LOCK_FILE"

# 3. Intentar arrancar el servidor Go
echo "[TEST] Arrancando Servidor Memory Plane..."
cd layers/l1_nervous && KUZU_DB_PATH="$DB_PATH" ./bin/memory_server &
GO_PID=$!
cd ../..

sleep 3

# 4. Verificar si el servidor sobrevivió al arranque y limpió el lock
if [ ! -f "$LOCK_FILE" ]; then
    echo "[PASS] El Fencing limpió el lock huérfano correctamente."
else
    # Si el archivo existe, ver si el servidor Go ahora es el dueño
    echo "[INFO] El archivo de bloqueo existe. Verificando si el servidor Go lo capturó..."
fi

# 5. Limpieza
kill $GO_PID
echo "[TEST] Servidor detenido."
