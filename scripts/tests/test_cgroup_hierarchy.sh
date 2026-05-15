#!/usr/bin/env bash
# TDD para Phase 1: Cgroups Hierarchy

set -euo pipefail

echo "=== Ejecutando Suite TDD: Gobernanza Cgroup (Spec 52) ==="

function assert_slice_exists() {
    local slice=$1
    if systemctl list-units --type=slice | grep -q "$slice"; then
        echo "[PASS] Slice '$slice' está cargado en Systemd."
    else
        echo "[FAIL] Slice '$slice' no fue encontrado."
        exit 1
    fi
}

function assert_ollama_cgroup() {
    # Verifica si Ollama pertenece al agentic.slice
    if ! systemctl is-active --quiet ollama; then
        echo "[WARN] Ollama no está corriendo. Omitiendo validación de su cgroup."
        return 0
    fi
    
    local cgroup=$(systemctl show -p ControlGroup ollama | cut -d= -f2)
    if [[ "$cgroup" == *"/agentic.slice/"* ]]; then
        echo "[PASS] Ollama corre bajo el ControlGroup correcto: $cgroup"
    else
        echo "[FAIL] Ollama corre fuera de los límites de DUMMIE: $cgroup"
        exit 1
    fi
}

assert_slice_exists "agentic.slice"
assert_ollama_cgroup

echo "=== Todos los Tests TDD [Phase 1] han Pasado ==="
