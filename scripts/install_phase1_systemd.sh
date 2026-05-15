#!/usr/bin/env bash
# Despliegue de Fase 1: Cgroups

set -euo pipefail

echo "[*] Instalando topología de Slices de Systemd..."

# 1. Copiar Slice principal
sudo cp "scripts/systemd/agentic.slice" "/etc/systemd/system/agentic.slice"

# 2. Copiar Template de Agentes
sudo cp "scripts/systemd/agentic-agent@.service" "/etc/systemd/system/agentic-agent@.service"

# 3. Subyugar Ollama
sudo mkdir -p "/etc/systemd/system/ollama.service.d"
sudo cp "scripts/systemd/ollama.service.d/99-agentic.conf" "/etc/systemd/system/ollama.service.d/99-agentic.conf"

# 4. Habilitar la delegación de CPU y Memory para el usuario (Permitir User Slices)
# Necesitamos permitir que el usuario use estos controladores si vamos a hacer systemd-run --user
sudo mkdir -p /etc/systemd/system/user@.service.d/
sudo tee /etc/systemd/system/user@.service.d/delegate.conf >/dev/null <<EOF
[Service]
Delegate=cpu cpuset memory io pids
EOF

# Recargar Daemons
echo "[*] Recargando configuración de Systemd Host..."
sudo systemctl daemon-reload

echo "[✓] Instalación Fase 1 Completada. Ejecuta 'bash scripts/tests/test_cgroup_hierarchy.sh' para validar."
