---
spec_id: DE-V2-L2-82
title: Long-Running Mission Runtime
status: ACTIVE
layer: L2
last_verified_on: '2026-05-15'
version: 1.0.0
namespace: dummie.engine.l2
---
# Long-Running Mission Runtime

## Purpose
Define the first runtime that lets DUMMIE start, pause, resume, block, complete, and recover multi-phase missions without losing state across sessions.

## Current State
Implemented in `layers/l2_brain/long_running_mission.py`. The runtime delegates persistence and state reconstruction to `PhaseLedger` and does not keep a parallel mutable state store.

## Physical Evidence
- `layers/l2_brain/long_running_mission.py`
- `layers/l2_brain/phase_ledger.py`
- `layers/l2_brain/daemon/daemon.py`
- `layers/l2_brain/tests/test_long_running_mission.py`
- `.aiwg/schemas/long_running_mission.schema.json`
- `.aiwg/missions/demo_refactor_snowball/phase_ledger.jsonl`
- `.aiwg/missions/demo_refactor_snowball/current_state.json`
- `.aiwg/missions/demo_refactor_snowball/recovery_packet.md`
- `.aiwg/missions/demo_refactor_snowball/next_action.json`

## Contract Invariants
- **Ledger SSoT**: The runtime must use `PhaseLedger` for lifecycle events and current state reconstruction.
- **Dependency Detection**: Starting a phase with incomplete dependencies must create a blocked phase event.
- **Checkpoint Before Completion**: Completing a phase must create a checkpoint first; if checkpoint creation fails, completion is not recorded.
- **Recovery Packet**: Runtime recovery must produce a public recovery packet and next action artifact.
- **Daemon Compatibility**: The daemon may attach current mission state to outcomes when `mission_runtime` is available and must still build outcomes without it.
- **Scope Boundary**: This runtime does not implement swarm, BrowserAgent, n8n, Workbench, Vault, or Kuzu persistence.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/82_long_running_mission_runtime.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_long_running_mission.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Ledger SSoT | `layers/l2_brain/long_running_mission.py` | `layers/l2_brain/tests/test_long_running_mission.py` |
| Dependency Detection | `layers/l2_brain/long_running_mission.py` | `layers/l2_brain/tests/test_long_running_mission.py` |
| Checkpoint Before Completion | `layers/l2_brain/long_running_mission.py` | `layers/l2_brain/tests/test_long_running_mission.py` |
| Recovery Packet | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_long_running_mission.py` |
| Daemon Compatibility | `layers/l2_brain/daemon/daemon.py` | `layers/l2_brain/tests/test_long_running_mission.py` |
| Scope Boundary | `doc/specs/82_long_running_mission_runtime.md` | `python3 scripts/validate_specs_docs.py` |
