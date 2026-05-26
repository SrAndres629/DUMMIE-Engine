---
spec_id: DE-PHASE6-TCL-83
title: Token Cost Ledger
status: DRAFT
layer: L2
last_verified_on: '2025-05-15'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.l2
claims:
- id: 83_token_cost_ledger-file-valid
  description: Spec file '83_token_cost_ledger.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/83_token_cost_ledger.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Token Cost Ledger

## Purpose
Provide a persistent, append-only record of cognitive costs (tokens) consumed by the DUMMIE Engine, categorized by session, mission, and phase.

## Current State
Implemented in `layers/l2_brain/token_cost_ledger.py`. Supports recording usage events, summarizing costs per mission/session/phase, and calculating cache hit ratios.

## Physical Evidence
- `layers/l2_brain/token_cost_ledger.py`
- `layers/l2_brain/tests/test_token_cost_ledger.py`
- `.aiwg/schemas/token_cost_ledger.schema.json`
- `.aiwg/missions/demo_refactor_snowball/token_cost_ledger.jsonl`

## Contract Invariants
- **Append Only**: Cost history is recorded as JSONL events.
- **Concurrency Safe**: Advisory file locking for concurrent writes using `fcntl`.
- **Idempotency**: Events with duplicate `event_id` are ignored.
- **Path Safety**: Rejects path traversal in `mission_id` and `session_id`.
- **No Private Reasoning**: Rejects payloads containing private reasoning or secrets.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/83_token_cost_ledger.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_token_cost_ledger.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Append Only | `layers/l2_brain/token_cost_ledger.py` | `layers/l2_brain/tests/test_token_cost_ledger.py` |
| Concurrency Safe | `layers/l2_brain/token_cost_ledger.py` | `layers/l2_brain/tests/test_token_cost_ledger.py` |
| Idempotency | `layers/l2_brain/token_cost_ledger.py` | `layers/l2_brain/tests/test_token_cost_ledger.py` |
| Path Safety | `layers/l2_brain/token_cost_ledger.py` | `layers/l2_brain/tests/test_token_cost_ledger.py` |
| No Private Reasoning | `layers/l2_brain/token_cost_ledger.py` | `layers/l2_brain/tests/test_token_cost_ledger.py` |
