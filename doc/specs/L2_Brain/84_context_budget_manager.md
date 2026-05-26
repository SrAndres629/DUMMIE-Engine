---
spec_id: DE-PHASE6-CBM-84
title: Context Budget Manager
status: DRAFT
layer: L2
last_verified_on: '2025-05-15'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.l2
claims:
- id: 84_context_budget_manager-file-valid
  description: Spec file '84_context_budget_manager.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/84_context_budget_manager.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Context Budget Manager

## Purpose
Manage the cognitive context window by allocating budgets, detecting pressure, and enforcing limits through selective discarding of low-priority information.

## Current State
Implemented in `layers/l2_brain/context/context_budget_manager.py`. Supports tiered budgets, pressure detection, and budget enforcement.

## Physical Evidence
- `layers/l2_brain/context/context_budget_manager.py`
- `layers/l2_brain/tests/test_context_budget_manager.py`
- `.aiwg/schemas/context_budget.schema.json`

## Contract Invariants
- **Preserve Critical**: Never discard items marked as 'critical' priority.
- **Tiered Budget**: Budgets vary based on `model_tier`.
- **Sequential Discard**: Discard low priority items first.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/84_context_budget_manager.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_context_budget_manager.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Preserve Critical | `layers/l2_brain/context/context_budget_manager.py` | `layers/l2_brain/tests/test_context_budget_manager.py` |
| Tiered Budget | `layers/l2_brain/context/context_budget_manager.py` | `layers/l2_brain/tests/test_context_budget_manager.py` |
| Sequential Discard | `layers/l2_brain/context/context_budget_manager.py` | `layers/l2_brain/tests/test_context_budget_manager.py` |
