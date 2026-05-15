#!/bin/bash
# DUMMIE Engine - Full Factory Launcher (Hardened)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
SOCKET_PATH="${MEMORY_SOCKET_PATH:-$AIWG_DIR/sockets/flight.sock}"
DUMMIED_SOCKET_PATH="${DUMMIE_DUMMIED_SOCKET_PATH:-$AIWG_DIR/sockets/dummied.sock}"
LEGACY_DUMMIED_SOCKET_PATH="$AIWG_DIR/dummied.sock"
# [HARDENING] Path canónico alineado con SOVEREIGN-4D
KUZU_PATH="${DUMMIE_KUZU_DB_PATH:-$AIWG_DIR/memory/loci.db}"
BIN_DIR="$ROOT_DIR/bin"
LOG_DIR="$ROOT_DIR/logs"

mkdir -p "$LOG_DIR"

echo "=== [FACTORY] Iniciando DUMMIE Engine (Nivel 5) ==="

# 1. Higiene Transaccional (Full Reset)
echo ">> Ensuring clean state..."
bash "$ROOT_DIR/scripts/shutdown_factory.sh"

mkdir -p "$AIWG_DIR/sockets"
mkdir -p "$(dirname "$KUZU_PATH")"

# 2. Iniciar L0 Supervisor (Control Plane Unificado) vía Systemd
echo ">> Provisioning Systemd User Service..."
mkdir -p "$HOME/.config/systemd/user"
cp "$ROOT_DIR/scripts/dummie-engine.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable dummie-engine.service 2>/dev/null || true
systemctl --user start dummie-engine.service

echo "[✓] Factory is ONLINE (Managed by systemd)."
echo "Sockets: $DUMMIED_SOCKET_PATH, $SOCKET_PATH"
echo "Kuzu: $KUZU_PATH"
