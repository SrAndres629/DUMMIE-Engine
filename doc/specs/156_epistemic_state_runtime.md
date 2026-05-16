---
spec_id: "156_epistemic_state_runtime"
title: "156 Epistemic State Runtime"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 156: Epistemic State Runtime

## Purpose
Classifies statements and evidence strength.

## Scope
- Categorizes knowledge claims to maintain epistemic humility.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/epistemic_state_runtime.py`
- `.aiwg/reports/epistemic_state_latest.json`
- `.aiwg/schemas/epistemic_state.schema.json`

## Contract Invariants
- lowers confidence on degraded runtime
- KNOWN requires passing tests or code evidence

## Verification
```bash
python3 layers/l2_brain/epistemic_state_runtime.py
pytest layers/l2_brain/tests/test_epistemic_state_runtime.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5_2 Module 1
