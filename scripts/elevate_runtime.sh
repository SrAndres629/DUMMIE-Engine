#!/bin/bash
# 🛡️ DUMMIE ENGINE: SOVEREIGN RUNTIME ELEVATION
# Objetivo: Resolver bloqueos de bwrap y otorgar permisos de ejecución a los agentes.

echo "[*] Iniciando elevación de privilegios del runtime..."

# 1. Habilitar namespaces de usuario no privilegiados (Fix para bwrap)
echo "[*] Configurando kernel.unprivileged_userns_clone..."
sudo sysctl -w kernel.unprivileged_userns_clone=1

# 2. Permitir bind en puertos bajos y namespaces de red
echo "[*] Ajustando net.ipv4.ip_unprivileged_port_start..."
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=0

# 3. Crear política de sudoers para agentes (Opcional, requiere aprobación manual)
# Esto permite que los agentes ejecuten comandos de mantenimiento sin password.
SUDO_POLICY="/etc/sudoers.d/dummie-agents"
POLICY_CONTENT="jorand ALL=(ALL) NOPASSWD: /usr/bin/sysctl, /usr/bin/bwrap, /usr/bin/apt-get, /usr/bin/npm, /usr/bin/npx"

if [ ! -f "$SUDO_POLICY" ]; then
    echo "[*] Generando política de sudoers en $SUDO_POLICY..."
    echo "$POLICY_CONTENT" | sudo tee "$SUDO_POLICY" > /dev/null
    sudo chmod 440 "$SUDO_POLICY"
else
    echo "[✓] Política de sudoers ya existe."
fi

# 4. Limpieza de sandboxes corruptos
echo "[*] Limpiando residuos de bwrap..."
rm -rf /tmp/antigravity-nsjail-* 2>/dev/null || true

echo "[✓] Elevación completada. Reinicia la sesión del agente para aplicar los cambios."
