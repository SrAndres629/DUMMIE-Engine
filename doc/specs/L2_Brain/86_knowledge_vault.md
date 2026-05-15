---
spec_id: DE-PHASE7-VLT-86
title: Knowledge Vault
status: DRAFT
layer: L2
last_verified_on: '2025-05-15'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.l2
---
# Knowledge Vault

## Purpose
Provide a central, curated repository under `.aiwg/vault/` for storing reusable knowledge, lessons learned, and proven patterns extracted from mission workbenches.

## Current State
Implemented in `layers/l2_brain/vault_curator.py`. Supports entry extraction, storage, indexing, and cleanup of mission workbenches.

## Physical Evidence
- `layers/l2_brain/vault_curator.py`
- `layers/l2_brain/tests/test_vault_curator.py`
- `.aiwg/schemas/vault_entry.schema.json`
- `.aiwg/vault/vault_index.json`

## Contract Invariants
- **Curated Knowledge**: Only valuable, non-redundant information should be stored in the vault.
- **No Private Reasoning**: Rejects entries containing private reasoning, secrets, or raw credentials.
- **Traceability**: All vault entries must reference their source mission and evidence.
- **Atomic Index**: The `vault_index.json` must be updated atomically.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/86_knowledge_vault.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_vault_curator.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Curated Knowledge | `layers/l2_brain/vault_curator.py` | `layers/l2_brain/tests/test_vault_curator.py` |
| No Private Reasoning | `layers/l2_brain/vault_curator.py` | `layers/l2_brain/tests/test_vault_curator.py` |
| Traceability | `layers/l2_brain/vault_curator.py` | `layers/l2_brain/tests/test_vault_curator.py` |
| Atomic Index | `layers/l2_brain/vault_curator.py` | `layers/l2_brain/tests/test_vault_curator.py` |
