#!/bin/bash
# DUMMIE Engine - Log Manager & Hygiene
# Prevents log explosion and manages disk space.

MAX_SIZE=10485760 # 10MB
LOGS=("l0.log" "l1.log")

echo "[HYGIENE] Starting log rotation check..."

for log in "${LOGS[@]}"; do
    if [ -f "$log" ]; then
        SIZE=$(stat -c%s "$log")
        if [ "$SIZE" -gt "$MAX_SIZE" ]; then
            echo "[HYGIENE] Rotating $log (Size: $SIZE bytes)"
            mv "$log" "$log.old"
            touch "$log"
        fi
    fi
done

# Limpieza de temporales de NSJail (si quedaron residuos)
rm -rf /tmp/antigravity-nsjail-* 2>/dev/null || true

echo "[HYGIENE] System is clean."
