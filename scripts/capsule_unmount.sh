#!/bin/bash
# capsule_unmount.sh — Canonical DUMMIE cognitive capsule clean unmount
# Spec: docs/superpowers/plans/2026-05-25-kernel-native-integration.md

set -e

MOUNT_BASE="${1:-/opt/dummie-engine/.aiwg/cognitive}"

echo "[capsule] Unmounting DUMMIE cognitive capsule from $MOUNT_BASE"

# Unmount tmpfs filesystems (ignore errors if not mounted)
for mnt in pulse sockets runtime; do
  umount "$MOUNT_BASE/$mnt" 2>/dev/null && \
    echo "[capsule]   $mnt/ unmounted" || \
    echo "[capsule]   $mnt/ not mounted (skip)"
done

# Remove symlinks
find "$MOUNT_BASE" -maxdepth 1 -type l -exec rm -f {} \; 2>/dev/null || true

# Remove mount base if empty
rmdir "$MOUNT_BASE" 2>/dev/null && \
  echo "[capsule]   Mount point removed" || \
  echo "[capsule]   Mount point not empty (skip)"

echo "[capsule] DUMMIE cognitive capsule unmounted"
