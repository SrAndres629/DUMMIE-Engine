---
spec_id: 152_cognitive_frame_builder
title: 152 Cognitive Frame Builder
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_5
last_verified_on: '2026-05-16'
claims:
- id: 152_cognitive_frame_builder-file-valid
  description: Spec file '152_cognitive_frame_builder.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/152_cognitive_frame_builder.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 152: Cognitive Frame Builder

## Purpose
Constructs safe execution context frames.

## Scope
- Enforces must_preserve rules and evidence-backed dispatch recommendations.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/cognition/cognitive_frame_builder.py`
- `.aiwg/reports/cognitive_frame_latest.json`
- `.aiwg/schemas/cognitive_frame.schema.json`

## Contract Invariants
- must preserve sovereign identity
- prohibits secrets and private reasoning

## Verification
```bash
pytest layers/l2_brain/tests/test_cognitive_frame_builder.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5 Module 3
