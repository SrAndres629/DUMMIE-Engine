#!/bin/bash
# DUMMIE Engine - Auto-Provisioning Wrapper
# Restringido vía /etc/sudoers.d/dummie-agent

ALLOWED_COMMANDS=("apt-get update" "apt-get install -y" "snap install" "flatpak install")

COMMAND="$1"
ARGS="${@:2}"

if [ -z "$COMMAND" ]; then
    echo "Uso: provision.sh <comando> [argumentos]"
    exit 1
fi

# Validar comandos permitidos
VALID=false
for allowed in "${ALLOWED_COMMANDS[@]}"; do
    if [[ "$COMMAND $ARGS" == *"$allowed"* ]]; then
        VALID=true
        break
    fi
done

if [ "$VALID" = false ]; then
    echo "❌ Operación NO permitida por la política de seguridad DUMMIE."
    exit 1
fi

echo "🚀 Ejecutando comando privilegiado aprobado: $COMMAND $ARGS"
sudo $COMMAND $ARGS
