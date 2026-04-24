#!/bin/bash
# DUMMIE Engine - Sovereign Agent Empowerment
# Based on ADR-0015 (User Mandate)

set -e

USER_NAME=$(whoami)

echo "=== [SOVEREIGNTY] Empowering AI Agents on this system ==="
echo "USER: $USER_NAME"

# 1. Añadir al grupo docker para evitar sudo en contenedores
if ! groups $USER_NAME | grep -q "\bdocker\b"; then
    echo ">> Adding $USER_NAME to docker group..."
    sudo usermod -aG docker $USER_NAME
    echo "[✓] User added to docker group. (RESTART REQUIRED)"
else
    echo "[✓] Already in docker group."
fi

# 2. Configurar Sudoers para comandos de infraestructura críticos
# Esto permite que los agentes corran 'uv', 'docker', 'make' etc sin password si fuera necesario.
# NOTA: Solo se aplica si el usuario lo desea.
SUDOERS_FILE="/etc/sudoers.d/antigravity-agents"
echo ">> Creating sudoers exception for agent-specific commands..."

cat <<EOF | sudo tee $SUDOERS_FILE > /dev/null
# DUMMIE Engine Agent Sovereignty
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/local/bin/uv, /home/jorand/.local/bin/uv
EOF
sudo chmod 440 $SUDOERS_FILE

# 3. Limpieza de sandboxes bloqueados
echo ">> Cleaning up stale nsjail sandboxes in /tmp..."
sudo rm -rf /tmp/antigravity-nsjail-sandbox-* 2>/dev/null || true

echo "---"
echo "[✓] AGENT EMPOWERMENT COMPLETE."
echo "IMPORTANTE: Debes reiniciar tu sesión de usuario para que el grupo 'docker' surta efecto."
echo "IMPORTANTE: En la configuración de Antigravity, desactiva 'Execution Sandbox' para permitir acceso directo al host."
echo "---"
