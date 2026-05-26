#!/bin/bash
# capsule_mount.sh — Canonical DUMMIE cognitive capsule mount system
# Spec: docs/superpowers/plans/2026-05-25-kernel-native-integration.md
# Systemd: dummie-capsule.service
# Source of Truth: .aiwg/ (hybrid tmpfs + disk)

set -e

AIWG_ROOT="${1:-/opt/dummie-engine/.aiwg}"
MOUNT_BASE="${2:-$AIWG_ROOT/cognitive}"

echo "[capsule] Mounting DUMMIE cognitive capsule..."
echo "[capsule]   Root: $AIWG_ROOT"
echo "[capsule]   Mount: $MOUNT_BASE"

# Create mount base
mkdir -p "$MOUNT_BASE"

# Ephemeral state — tmpfs (RAM, lost on unmount)
mkdir -p "$MOUNT_BASE/runtime" && \
  mount -t tmpfs -o size=256M,mode=755 tmpfs-cog-runtime "$MOUNT_BASE/runtime" && \
  echo "[capsule]   runtime/ : tmpfs 256M"

mkdir -p "$MOUNT_BASE/sockets" && \
  mount -t tmpfs -o size=64M,mode=755 tmpfs-cog-sockets "$MOUNT_BASE/sockets" && \
  echo "[capsule]   sockets/ : tmpfs 64M"

mkdir -p "$MOUNT_BASE/pulse" && \
  mount -t tmpfs -o size=128M,mode=755 tmpfs-cog-pulse "$MOUNT_BASE/pulse" && \
  echo "[capsule]   pulse/   : tmpfs 128M"

# Persistent state — disk symlinks to canonical .aiwg
for dir in state memory identity sessions registry heartbeat memory mental_models decisions; do
  if [ -d "$AIWG_ROOT/$dir" ]; then
    ln -sf "$AIWG_ROOT/$dir" "$MOUNT_BASE/$dir" 2>/dev/null || true
  fi
done
echo "[capsule]   Persistent state directories symlinked"

# Permissions
chown -R jorand:jorand "$MOUNT_BASE" 2>/dev/null || true

echo "[capsule] DUMMIE cognitive capsule mounted at $MOUNT_BASE"
