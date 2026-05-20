---
spec_id: "191_whole_body_repair_queue"
title: "Whole Body Repair Queue"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
Convert full-body audits and capability promotion reports into a prioritized, evidence-backed queue of actionable repairs, ensuring safety and truth gates are addressed before scaling autonomy.

## Current State
Under implementation.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/whole_body_repair_queue.py`
- Test suite: `layers/l2_brain/tests/test_whole_body_repair_queue.py`
- JSON Schema: `.aiwg/schemas/whole_body_repair_queue.schema.json`
- Output reports: `.aiwg/reports/whole_body_repair_queue_latest.json` and `.aiwg/reports/whole_body_repair_queue_latest.md`

## Contract Invariants
- **Evidence-Driven Priority**: Priority must place false truth claims first, followed by memory (Kùzu readback) and embedding issues, before any new agentic capabilities or workflows.
- **Accurate Action Modeling**: Each action must map to a specific body part, define verification steps, and mark human approval requirements.
- **Safe Execution Guards**: Actions must not execute autonomously unless explicit conditions are satisfied.

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_whole_body_repair_queue.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `whole_body_repair_queue.schema.json`
