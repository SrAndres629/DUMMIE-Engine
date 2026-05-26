---
spec_id: 150_mental_model_runtime
title: 150 Mental Model Runtime
status: DEPRECATED
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_5
last_verified_on: '2026-05-16'
claims:
- id: 150_mental_model_runtime-file-valid
  description: Spec file '150_mental_model_runtime.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/150_mental_model_runtime.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 150: Mental Model Runtime

## Purpose
Evidence-backed structured abstraction of intent context.

## Scope
- Extracts entities, relations, risks, and contradictions from repo reports and intent.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `.aiwg/reports/mental_model_runtime_latest.json`
- `.aiwg/schemas/mental_model.schema.json`

## Contract Invariants
- relations cannot be empty for complex intents
- must penalize score for degraded status

## Verification
```bash
pytest layers/l2_brain/tests/test_mental_model_runtime.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5 Module 1
