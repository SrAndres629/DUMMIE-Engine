---
spec_id: "155_metacognitive_quality_gate"
title: "155 Metacognitive Quality Gate"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 155: Metacognitive Quality Gate

## Purpose
Audits the quality of the thinking process.

## Scope
- Evaluates model, ontology and frame completeness and safety.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/flat_brain/metacognitive_quality_gate.py`
- `.aiwg/reports/metacognitive_quality_gate_latest.json`
- `.aiwg/schemas/metacognitive_quality_gate.schema.json`

## Contract Invariants
- limits quality score to 70 if degraded status
- limits quality score to 50 if bias FAIL

## Verification
```bash
pytest layers/l2_brain/tests/test_metacognitive_quality_gate.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5 Module 6
