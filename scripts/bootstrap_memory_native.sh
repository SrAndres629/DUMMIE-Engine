#!/bin/bash
# scripts/bootstrap_memory_native.sh
set -e

VERSION="v0.11.3"
ROOT_DIR="$(pwd)"
TARGET_DIR="$ROOT_DIR/shared/lib/kuzu"

echo "=== [L0-INFRA] Descargando Kùzu Native ($VERSION) ==="
mkdir -p "$TARGET_DIR"

# URL de la release de C++ (que contiene las .so y headers)
URL="https://github.com/kuzudb/kuzu/releases/download/$VERSION/libkuzu-linux-x86_64.tar.gz"

TEMP_FILE="kuzu_native.tar.gz"
curl -L "$URL" -o "$TEMP_FILE"

# Extraer solo lo necesario (esta versión no tiene subcarpeta)
tar -xzf "$TEMP_FILE" -C "$TARGET_DIR"
rm "$TEMP_FILE"

echo "[✓] Librerías nativas instaladas en: $TARGET_DIR"
ls -F "$TARGET_DIR"
