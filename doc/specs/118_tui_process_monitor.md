---
spec_id: "DE-V2-L2-118"
title: "TUI Process Monitor"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 118 - TUI Process Monitor

## Purpose
Provide deterministic textual monitoring of runtime status without external UI dependencies.

## Scope
Covers snapshot building and text rendering from canonical and latest runtime artifacts.

## Runtime Behavior
Builds `ProcessMonitorSnapshot` and text panel with phase, gate, flywheel, benchmark, cache, stale findings, and recommended action.

## Inputs
Current state, next seed, restart gate latest, benchmark latest, flywheel latest, cache summary, stale memory report, context quant result.

## Outputs
- `.aiwg/reports/process_monitor_latest.json`
- `.aiwg/reports/process_monitor_latest.txt`

## Safety Rules
No crash on optional missing artifacts; warnings must be explicit.

## Missing Artifact Behavior
Missing optional artifact -> warning; critical state mismatch can degrade decision to FAIL.

## Relationship to P10-P17
Reads P10-P17 artifacts and exposes operational status for human/agent control loops.

## Current State
Implemented in `layers/l2_brain/tui_process_monitor.py`.

## Physical Evidence
- `layers/l2_brain/tui_process_monitor.py`
- `.aiwg/reports/process_monitor_latest.json`
- `.aiwg/reports/process_monitor_latest.txt`

## Contract Invariants
- Snapshot and text outputs are deterministic for fixed artifacts.
- Output includes phase and next phase lines.

## Tests Expected
`test_tui_process_monitor.py` and integration test must pass.

## Verification
```bash
git diff --check
pytest -q layers/l2_brain/tests/test_tui_process_monitor.py
```

## Traceability
Upstream: CLI and runtime latest outputs. Downstream: dashboard renderer and operator workflows.
