---
spec_id: 186_dependency_reproducibility_verifier
title: Dependency Reproducibility Verifier
status: DEPRECATED
layer: L2
last_verified_on: '2026-05-16'
claims:
- id: 186_dependency_reproducibility_verifier-file-valid
  description: Spec file '186_dependency_reproducibility_verifier.md' exists, parses
    valid YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/186_dependency_reproducibility_verifier.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Ensure all physically installed python packages in the active virtual environment are properly registered in the project's dependency declarations to prevent accidental runtime state divergence.

## Current State
Under implementation.

## Physical Evidence
- Test suite: `layers/l2_brain/tests/test_dependency_reproducibility_verifier.py`
- JSON Schema: `.aiwg/schemas/dependency_reproducibility.schema.json`
- Output reports: `.aiwg/reports/dependency_reproducibility_latest.json` and `.aiwg/reports/dependency_reproducibility_latest.md`

## Contract Invariants
- **Verification Integrity**: If heavy packages (like torch/sentence-transformers) are installed but not declared in `pyproject.toml`, the decision cannot be `PASS`.
- **Zero Mutative Operations**: Audits log all operations. Package writes require explicit contract authorization and evidence trail.
- **Accurate Heavy Footprint Recording**: The footprint sizes of heavy dependencies must be tracked.

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_dependency_reproducibility_verifier.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `dependency_reproducibility.schema.json`
