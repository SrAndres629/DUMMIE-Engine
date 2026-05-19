---
spec_id: "181_runtime_closure_planner"
title: "Runtime Closure Planner"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the runtime closure planner (HEARTBEAT-2.1) to translate degraded capabilities into sequential, human-executable closure recipes and dependency resolution paths.

## Current State
Under implementation. Will process degraded capability registry reports and output validated closure plans conforming to `runtime_closure_plan.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/runtime_closure_planner.py`
- Test suite: `layers/l2_brain/tests/test_runtime_closure_planner.py`
- JSON Schema: `.aiwg/schemas/runtime_closure_plan.schema.json`
- Output reports: `.aiwg/reports/runtime_closure_plan_latest.json` and `.aiwg/reports/runtime_closure_plan_latest.md`

## Contract Invariants
- **Strict Human Authorization Gate**: Any action of type `install_dependency` MUST be set to `can_execute_now: false` and `requires_human_approval: true`. Auto-installing is strictly forbidden.
- **Action Structure**: Actions must detail exact `commands_to_run`, `files_to_modify`, `verification_commands`, `rollback_plan`, and `risk_level`.
- **Kùzu Repair Sequence**: The plan for resolving `kuzu_4dtes_persistence` must sequentialize: package installation check, import verification, database path calibration, local sandbox write simulation, and final recovery validation.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_runtime_closure_planner.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.1)
- Contract Schema: `runtime_closure_plan.schema.json`
