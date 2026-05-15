#!/usr/bin/env bash
# TDD para Phase 2: ZRAM & Swap

set -euo pipefail

echo "=== Ejecutando Suite TDD: Kernel Memory (Spec 52) ==="

function assert_zram() {
    if zramctl --output-all | grep -q "zram0"; then
        echo "[PASS] Dispositivo zram0 existe."
        if zramctl --output-all | grep "zram0" | grep -q "zstd"; then
            echo "[PASS] ZRAM usa algoritmo zstd."
        else
            echo "[FAIL] ZRAM no usa zstd."
            exit 1
        fi
    else
        echo "[FAIL] ZRAM0 no configurado."
        exit 1
    fi
}

function assert_swap() {
    if swapon --show | grep -q "/var/lib/swapfile-agentic"; then
        echo "[PASS] Fallback swap activo."
    else
        echo "[FAIL] Fallback swap no activo."
        exit 1
    fi
}

assert_zram
assert_swap
echo "=== Todos los Tests TDD [Phase 2] han Pasado ==="
