---
spec_id: 210_tmpfs_aiwg_ephemeral
title: tmpfs for .aiwg Ephemeral Data
status: ACTIVE
layer: L1
last_verified_on: '2026-05-25'
claims:
- id: 210_tmpfs_aiwg_ephemeral-file-valid
  description: Spec file '210_tmpfs_aiwg_ephemeral.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/210_tmpfs_aiwg_ephemeral.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Move ephemeral .aiwg directories (runtime, reports, sockets) to RAM-backed tmpfs. Currently these directories live on `/media/datasets/` (NTFS via fuseblk), adding FUSE serialization latency to every read/write. tmpfs eliminates disk I/O for transient data that has no persistence value.

## Current State
- `.aiwg/runtime` — 16KB, gateway readiness markers and PIDs, recreated every boot
- `.aiwg/reports` — 98MB, JSON/MD runtime reports, regenerated every session
- `.aiwg/sockets` — empty, reserved for Unix sockets
- Parent filesystem: NTFS (fuseblk) via /media/datasets/

## Physical Evidence
```bash
mount | grep /media/datasets
# /dev/nvme0n1p7 on /media/datasets type fuseblk (rw,nosuid,nodev,noatime,...)
ls -la .aiwg/runtime/ .aiwg/reports/ .aiwg/sockets/
```

## Contract Invariants
- **Persistence**: tmpfs must be mounted before dummie-engine starts, unmounted after stop
- **Sizing**: runtime=256M, reports=512M, sockets=64M (all well within 16GB RAM)
- **Permissions**: Must be writable by the dummie-engine service user (root)
- **No data loss**: Only ephemeral data goes to tmpfs; persistent .aiwg data stays on NTFS

## Verification
```bash
mount | grep tmpfs-dummie
# tmpfs-dummie-runtime on .../runtime type tmpfs (rw,size=256M)
# tmpfs-dummie-reports on .../reports type tmpfs (rw,size=512M)
# tmpfs-dummie-sockets on .../sockets type tmpfs (rw,size=64M)
```

## Traceability
- Maps to: FDA-003 (Ephemeral I/O in RAM)
- Source changes: `dummie-engine.service.d/override.conf` (ExecStartPre/ExecStopPost for mount)
