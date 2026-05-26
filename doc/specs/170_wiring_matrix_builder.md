---
spec_id: 170_wiring_matrix_builder
title: Wiring Matrix Builder
status: DEPRECATED
layer: L2
last_verified_on: '2026-05-17'
claims:
- id: 170_wiring_matrix_builder-file-valid
  description: Spec file '170_wiring_matrix_builder.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/170_wiring_matrix_builder.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
This specification establishes the systemic wiring matrix mapping tool (HEARTBEAT-1.1). It parses imports, spec targets, test files, and schemas to generate a complete, bi-directional dependency graph across all first-party layers of the DUMMIE Engine.

## Current State
Fully implemented in the L2 Brain layer. Consumed by the metacognitive heartbeat to identify unwired code elements, spec gaps, and test debt.

## Physical Evidence
- Test suite: `layers/l2_brain/tests/test_wiring_matrix_builder.py`
- Output report JSON: `.aiwg/reports/wiring_matrix_latest.json`
- Output report Markdown: `.aiwg/reports/wiring_matrix_latest.md`

## Contract Invariants
- **Graph Nodes & Edges:** Every module, spec, test, and schema must be a distinct node. Directed edges represent imports, testing, mapping, or validation relationships.
- **Anomaly Detection:** Must detect unwired source modules, missing test files, orphaned specifications, and schemas without consumers.

## Verification
Run tests:
```bash
python3 -m pytest layers/l2_brain/tests/test_wiring_matrix_builder.py
```

## Traceability
- Maps to: Spec 168
- Contract Schema: `wiring_matrix.schema.json`
