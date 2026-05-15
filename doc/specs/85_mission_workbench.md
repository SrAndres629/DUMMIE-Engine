---
spec_id: "DE-PHASE7-MWB-85"
title: "Mission Workbench"
status: "DRAFT"
layer: "L2"
last_verified_on: "2025-05-15"
priority: "MANDATORY"
---
# Mission Workbench

## Purpose
Provide a per-mission operational workspace under `.aiwg/workbench/{mission_id}/` to store artifacts, logs, and state related to a specific mission's execution.

## Current State
Implemented in `layers/l2_brain/mission_workbench.py`. Supports workbench creation, artifact writing, decision logging, and integration with the Phase Ledger and Token Economy components.

## Physical Evidence
- `layers/l2_brain/mission_workbench.py`
- `layers/l2_brain/tests/test_mission_workbench.py`
- `.aiwg/schemas/mission_workbench.schema.json`
- `.aiwg/workbench/demo_refactor_snowball/objective.md`
- `.aiwg/workbench/demo_refactor_snowball/decision_log.jsonl`

## Contract Invariants
- **Mission Isolation**: Workspaces must be strictly partitioned by `mission_id`.
- **Path Safety**: Rejects path traversal and writes only under `.aiwg/workbench`.
- **No Private Reasoning**: Rejects payloads containing private reasoning, secrets, or raw credentials.
- **Traceability**: Integrates with Phase Ledger by recording workbench lifecycle events.
- **Persistence**: Finalized workbenches are retained by default for audit and curation.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/85_mission_workbench.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_mission_workbench.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Mission Isolation | `layers/l2_brain/mission_workbench.py` | `layers/l2_brain/tests/test_mission_workbench.py` |
| Path Safety | `layers/l2_brain/mission_workbench.py` | `layers/l2_brain/tests/test_mission_workbench.py` |
| No Private Reasoning | `layers/l2_brain/mission_workbench.py` | `layers/l2_brain/tests/test_mission_workbench.py` |
| Traceability | `layers/l2_brain/mission_workbench.py` | `layers/l2_brain/tests/test_mission_workbench.py` |
| Persistence | `layers/l2_brain/mission_workbench.py` | `layers/l2_brain/tests/test_mission_workbench.py` |
