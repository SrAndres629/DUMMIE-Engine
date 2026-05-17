---
spec_id: "168_whole_body_scanner"
title: "Whole-Body Scan, Wiring Matrix, and Shadow Detector Runtime"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the whole-body scan, wiring matrix mapping, and shadow runtime detection capability (HEARTBEAT-1) to scan the workspace and identify disconnected, stale, or orphaned assets.

## Current State
Fully implemented in Python ast-parsing runtime, integrated with the CLI control plane, DUMMIE chat engine, and the `dummie-ctl` script. Outputs scan indices, wiring completeness metrics, and anomaly logs.

## Physical Evidence
- Core module: `layers/l2_brain/whole_body_scanner.py`
- Test suite: `layers/l2_brain/tests/test_whole_body_scanner.py`
- CLI command: `layers/l2_brain/cli_control_plane.py` (handler method _cmd_whole_body_scan)
- Chat intent: `layers/l2_brain/dummie_chat_cli.py` (handler method _cmd_whole_body_scan)
- JSON Schema: `.aiwg/schemas/whole_body_scan.schema.json`
- Output reports: `.aiwg/reports/whole_body_scan_latest.json` and `.aiwg/reports/whole_body_scan_latest.md`

## Contract Invariants
- **Import Parsing:** Must parse python files and extract module imports.
- **Spec Mapping:** Must extract physical evidence files from all specification files.
- **Shadow Detection:** Any python file with no imports from other modules, not marked as a test or an entrypoint, and with 0 specs mapped is classified as `"orphaned"`.
- **Systemic Coherence:** Overall score must be an average of active (non-orphaned) coherence scores.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_whole_body_scanner.py
```
Execute manual scan via:
```bash
scripts/dummie-ctl scan
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-1)
- Contract Schema: `whole_body_scan.schema.json`
