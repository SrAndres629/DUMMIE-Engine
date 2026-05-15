#!/usr/bin/env bash
# Despliegue de Fase 2: Memoria ZRAM & Swap

set -euo pipefail

echo "[*] Instalando Gobernanza de Memoria del Kernel (Spec 52)..."

# 1. Sysctl Tuning
sudo cp "scripts/systemd/zz-agentic-memory.conf" "/etc/sysctl.d/zz-agentic-memory.conf"
sudo sysctl --system

# 2. Configurar ZRAM
if ! command -v zramctl &> /dev/null; then
    echo "[!] Instala zram-tools (sudo apt install zram-tools) para habilitar zram."
else
    # Escribir override de zram local
    echo "[*] Configurando zram0 (zstd, 75%)..."
    sudo tee /etc/default/zramswap >/dev/null <<EOF
ALGO=zstd
PERCENT=75
PRIORITY=100
EOF
    sudo systemctl restart zramswap || sudo systemctl restart systemd-zram-setup@zram0.service || true
fi

# 3. Crear Fallback Swap
SWAP_FILE="/var/lib/swapfile-agentic"
if [ ! -f "$SWAP_FILE" ]; then
    echo "[*] Creando archivo de swap de emergencia de 8GB..."
    sudo fallocate -l 8G "$SWAP_FILE"
    sudo chmod 600 "$SWAP_FILE"
    sudo mkswap "$SWAP_FILE"
    sudo swapon -p 1 "$SWAP_FILE"
    
    # Agregar a fstab si no existe
    if ! grep -q "$SWAP_FILE" /etc/fstab; then
        echo "$SWAP_FILE none swap sw,pri=1 0 0" | sudo tee -a /etc/fstab
    fi
else
    echo "[✓] Swapfile de emergencia ya existe."
fi

echo "[✓] Instalación Fase 2 Completada. Ejecuta 'bash scripts/tests/test_zram_hierarchy.sh' para validar."
