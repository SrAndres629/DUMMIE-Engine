---
spec_id: "175_4dtes_persistence_preflight"
title: "4D-TES Persistence Preflight"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the 4D-TES persistence preflight check (HEARTBEAT-2) to safely analyze the health of the Kùzu graph store and outline non-destructive repairs.

## Current State
Under implementation. Will diagnose the persistence layer and create action plans conforming to `4dtes_persistence_preflight.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/four_dtes_persistence_preflight.py`
- Test suite: `layers/l2_brain/tests/test_four_dtes_persistence_preflight.py`
- JSON Schema: `.aiwg/schemas/4dtes_persistence_preflight.schema.json`
- Output reports: `.aiwg/reports/4dtes_persistence_preflight_latest.json` and `.aiwg/reports/4dtes_persistence_preflight_latest.md`

## Contract Invariants
- **Non-destructive Auditing**: Preflight must only inspect files, configurations, and imports; no real Kùzu database write transactions may be executed.
- **Degraded Status Mapping**: If Kùzu is degraded or unavailable, decision must be `PASS_WITH_WARNINGS` or `FAIL` rather than an unconditional `PASS`, and `graph_write_mode` must be `DEGRADED`, `SIMULATED`, or `DRY_RUN_ONLY`.
- **System Integrity Guard**: Recommends repairs but blocks any action that requires manual dependencies or destructive mutations.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_four_dtes_persistence_preflight.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `4dtes_persistence_preflight.schema.json`
