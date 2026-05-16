---
spec_id: "153_metacognitive_loop_runtime"
title: "153 Metacognitive Loop Runtime"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 153: Metacognitive Loop Runtime

## Purpose
Orchestrates the thinking-before-answering cycle.

## Scope
- Integrates all metacognitive modules with a unified quality gate.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/metacognitive_loop_runtime.py`
- `.aiwg/reports/metacognitive_loop_latest.json`
- `.aiwg/schemas/metacognitive_loop.schema.json`

## Contract Invariants
- must call quality gate before final decision
- propagates downstream failures

## Verification
```bash
python3 layers/l2_brain/metacognitive_loop_runtime.py
pytest layers/l2_brain/tests/test_metacognitive_loop_runtime.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5 Module 4
