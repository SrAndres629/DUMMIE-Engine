---
spec_id: "160_metacognitive_evolution_flywheel"
title: "160 Metacognitive Evolution Flywheel"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 160: Metacognitive Evolution Flywheel

## Purpose
Performs belief revision and learning delta tracking.

## Scope
- Updates mental models based on dialectical feedback.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/flat_brain/metacognitive_evolution_flywheel.py`
- `.aiwg/reports/metacognitive_evolution_flywheel_latest.json`
- `.aiwg/schemas/metacognitive_evolution_flywheel.schema.json`

## Contract Invariants
- records learning deltas sequentially
- updates next actions based on epistemic state

## Verification
```bash
python3 layers/l2_brain/flat_brain/metacognitive_evolution_flywheel.py
pytest layers/l2_brain/tests/test_metacognitive_evolution_flywheel.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5_2 Module 5
