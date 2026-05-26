---
spec_id: 213_scx_layered_scheduling
title: sched_ext Layered Scheduler for Agentic OS
status: ACTIVE
layer: OS
last_verified_on: '2026-05-25'
claims:
- id: 213_scx_layered_scheduling-file-valid
  description: Spec file '213_scx_layered_scheduling.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/213_scx_layered_scheduling.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Deploy the sched_ext (BPF-based extensible scheduler) `scx_layered` scheduler to assign different scheduling policies per DUMMIE Engine layer. The OEM kernel 6.17.0-1023-oem has CONFIG_SCHED_CLASS_EXT=y built-in but no scheduler is loaded. Using scx_layered, L0 (overseer daemon) gets real-time priority, L1 (gateways/routing) gets latency-sensitive, L2 (brain/memory) gets throughput.

## Current State
- Kernel: OEM 6.17.0-1023-oem with CONFIG_SCHED_CLASS_EXT=y
- `/sys/kernel/sched_ext/` exists but empty — no scheduler loaded
- All dummie-engine processes run under `agentic-workload.slice` with default CFS
- `scx` tools not installed

## Physical Evidence
```bash
cat /boot/config-6.17.0-1023-oem | grep SCHED_CLASS_EXT
# CONFIG_SCHED_CLASS_EXT=y
ls /sys/kernel/sched_ext/  # empty (no ops registered)
systemctl cat dummie-engine.service | grep Slice
# Slice=agentic-workload.slice
```

## Contract Invariants
- **Loadable**: scx_layered must be installed without kernel recompilation (modprobe or signed module)
- **Stackable**: If sched_ext fails to load, fall back to CFS (no system crash)
- **Layer-aware**: Each layer (L0-L6) must map to a distinct scheduling policy via cgroup paths
- **Lightweight**: scx daemon must use <1% CPU when idle

## Verification
```bash
scx_layered --status 2>/dev/null && echo "sched_ext active" || echo "sched_ext not loaded"
cat /sys/kernel/sched_ext/ops 2>/dev/null | grep -q "layered"
ls /sys/fs/cgroup/agentic-workload.slice/ | grep cpu
```

## Traceability
- Maps to: FDA-004 (scheduler isolation)
- Source changes: systemd slices, scx package install, optional config file
