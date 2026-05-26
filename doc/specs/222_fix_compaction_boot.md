---
status: Approved
claims:
- id: compaction_correct
  description: vm.compaction_proactiveness es 20 en runtime
  severity: critical
- id: sysctl_single_file
  description: Archivo canonico unico zz-agentic-memory.conf
  severity: high
implementations:
  - file: /etc/sysctl.d/zz-agentic-memory.conf
    type: configuration
---

# Fix: compaction_proactiveness sysctl + boot persistence

**Date:** 2026-05-26
**Phase:** Post-reboot fix
**Requires reboot:** No

## Problem

`/etc/sysctl.d/99-low-latency.conf` tiene `compaction_proactiveness=20` en vez de `vm.compaction_proactiveness=20`. Esto causa error de parseo en `sysctl --system` durante el boot, impidiendo que **todos** los parámetros se apliquen (swappiness, watermarks, etc.).

Post-reboot, `compaction_proactiveness` está en 80 (default Ubuntu) en vez de 20.

## Fix

### File: `/etc/sysctl.d/99-low-latency.conf`

Change:
```
compaction_proactiveness=20
```
To:
```
vm.compaction_proactiveness=20
```

### Live application

```bash
sudo sysctl vm.compaction_proactiveness=20
sudo sysctl --system
```

### Verification

```bash
cat /proc/sys/vm/compaction_proactiveness  # must be 20
sudo sysctl --system 2>&1 | grep -c error  # must be 0
```