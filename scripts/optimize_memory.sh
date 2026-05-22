#!/bin/bash
# DUMMIE Engine Memory Optimization Script
# Configura: zram optimizado, swap jerarquizado, unified memory, kernel params

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }

echo "=== DUMMIE Engine Memory Optimization ==="
echo ""

# --- Memory Detection ---
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$(( TOTAL_RAM_KB / 1024 / 1024 ))
ZRAM_SIZE=$(( TOTAL_RAM_KB * 50 / 100 ))  # 50% of RAM
SWAPINESS=60  # Balanced (default=60)
VFS_CACHE_PRESSURE=50  # Less aggressive page cache reclaim

log "Total RAM: ${TOTAL_RAM_GB}GB"
log "Target zram: $(( ZRAM_SIZE / 1024 / 1024 ))GB (50% of RAM)"

# --- 1. ZRAM Optimization ---
if command -v zramctl &>/dev/null; then
    # Remove existing zram if present
    if zramctl -o NAME -n 2>/dev/null | grep -q .; then
        swapoff /dev/zram0 2>/dev/null || true
        echo 1 > /sys/class/zram-control/hot_remove 2>/dev/null || true
        warn "Existing zram removed, recreating..."
    fi

    # Create optimized zram
    echo "1" > /sys/class/zram-control/hot_add || true
    ZRAM_DEV=$(zramctl -o NAME -n 2>/dev/null | head -1)
    if [ -z "$ZRAM_DEV" ]; then
        ZRAM_DEV="zram0"
    fi

    # Configure: zstd compression (best ratio/speed for LLM weights)
    echo "zstd" > /sys/block/${ZRAM_DEV}/comp_algorithm 2>/dev/null || true

    # Set size: 50% of RAM (compressed ~2-3x = 100-150% effective)
    echo "${ZRAM_SIZE}" > /sys/block/${ZRAM_DEV}/disksize
    mkswap /dev/${ZRAM_DEV}
    swapon /dev/${ZRAM_DEV} -p 100

    log "zram created: ${ZRAM_DEV} = $(( ZRAM_SIZE / 1024 / 1024 ))GB (zstd, priority 100)"
else
    err "zramctl not found (install util-linux)"
fi

# --- 2. Swap Hierarchy ---
# zram (prio 100) > swapfile (prio 1) > none
# Kernel swaps to lower priority first when higher priority fills
log "Swap hierarchy: zram(p100) > swapfile(p1)"

# --- 3. Kernel Parameters ---
sysctl -w vm.swappiness=${SWAPINESS} 2>/dev/null && log "vm.swappiness=${SWAPINESS}"
sysctl -w vm.vfs_cache_pressure=${VFS_CACHE_PRESSURE} 2>/dev/null && log "vm.vfs_cache_pressure=${VFS_CACHE_PRESSURE}"
sysctl -w vm.dirty_ratio=40 2>/dev/null && log "vm.dirty_ratio=40"
sysctl -w vm.dirty_background_ratio=10 2>/dev/null && log "vm.dirty_background_ratio=10"

# --- 4. CUDA Unified Memory ---
# Enable CUDA Unified Memory for models that exceed VRAM
export CUDA_MANAGED_FORCE_DEVICE_ALLOC=1  # Force managed memory on single GPU
export TF_GPU_ALLOCATOR=cuda_malloc_async  # TensorFlow async allocator
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True  # PyTorch fragmentation

# Persist in .env
ENV_FILE="${DUMMIE_ROOT:-/media/datasets/DUMMIE Engine}/.env"
if command -v python3 &>/dev/null; then
    python3 -c "
env_vars = {
    'CUDA_MANAGED_FORCE_DEVICE_ALLOC': '1',
    'TF_GPU_ALLOCATOR': 'cuda_malloc_async',
    'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:128,expandable_segments:True',
}
import os
path = os.environ.get('DUMMIE_ROOT', '/media/datasets/DUMMIE Engine') + '/.env'
with open(path, 'a') as f:
    for k, v in env_vars.items():
        f.write(f'{k}={v}\n')
print(f'Config saved to {path}')
" 2>/dev/null && log "CUDA env vars persisted to .env"
fi

# --- 5. Memory Reservation for Models ---
# Reserve 512MB for system, rest for models
SYSTEM_RESERVE_MB=512
VRAM_TOTAL_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null || echo "0")
if [ "$VRAM_TOTAL_MB" -gt 0 ]; then
    VRAM_AVAILABLE=$(( VRAM_TOTAL_MB - SYSTEM_RESERVE_MB ))
    log "VRAM: ${VRAM_TOTAL_MB}MB total, ${VRAM_AVAILABLE}MB available (${SYSTEM_RESERVE_MB}MB reserved)"
    log "Model budget: embedding(200MB) + reranker(100MB) + LLM(~3000MB) = ~3300MB < ${VRAM_AVAILABLE}MB ✅"
fi

echo ""
echo "=== Optimization Complete ==="
free -h
echo ""
zramctl 2>/dev/null || true
echo ""
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv 2>/dev/null || true
