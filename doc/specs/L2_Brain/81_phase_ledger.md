---
spec_id: DE-V2-L2-81
title: Phase Ledger
status: ACTIVE
layer: L2
last_verified_on: '2026-05-15'
version: 1.0.0
namespace: dummie.engine.l2
---
# Phase Ledger

## Purpose
Define the append-only phase ledger that records mission and phase progress under `.aiwg/missions/{mission_id}/phase_ledger.jsonl`.

## Current State
Implemented in `layers/l2_brain/phase_ledger.py`. The ledger creates missions, records phase events, reconstructs current state from JSONL, writes checkpoints atomically, creates recovery packets, and persists next action artifacts.

## Physical Evidence
- `layers/l2_brain/phase_ledger.py`
- `layers/l2_brain/tests/test_phase_ledger.py`
- `.aiwg/schemas/phase_ledger.schema.json`
- `.aiwg/missions/demo_refactor_snowball/phase_ledger.jsonl`
- `.aiwg/missions/demo_refactor_snowball/current_state.json`
- `.aiwg/missions/demo_refactor_snowball/recovery_packet.md`
- `.aiwg/missions/demo_refactor_snowball/next_action.json`

## Contract Invariants
- **Append Only**: Mission history is recorded as JSONL events; state is reconstructed from the ledger, not treated as the source of truth.
- **Allowed Events**: Ledger events are restricted to mission, phase, checkpoint, recovery, next action, and terminal mission lifecycle events.
- **Path Safety**: `mission_id` and `phase_id` must reject path traversal and write only under `.aiwg/missions`.
- **Atomic Artifacts**: `current_state.json`, `next_action.json`, `recovery_packet.md`, and checkpoint files must be written atomically.
- **No Private Reasoning**: Ledger payloads must reject private chain-of-thought, `.env`, secrets, and credential references.
- **Canonical Authority**: Registered phase authority levels must match `layers/l2_brain/models.py`.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/81_phase_ledger.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_phase_ledger.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Append Only | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_phase_ledger.py` |
| Allowed Events | `.aiwg/schemas/phase_ledger.schema.json` | `layers/l2_brain/tests/test_phase_ledger.py` |
| Path Safety | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_phase_ledger.py` |
| Atomic Artifacts | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_phase_ledger.py` |
| No Private Reasoning | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_phase_ledger.py` |
| Canonical Authority | `layers/l2_brain/phase_ledger.py` | `layers/l2_brain/tests/test_phase_ledger.py` |
