---
spec_id: "161_mental_model_truth_hygiene"
title: "161 Mental Model Truth Hygiene"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5_2_2"
last_verified_on: "2026-05-16"
---

# Spec 161: Mental Model Truth Hygiene

## Purpose
Scan, classify, quarantine and audit all stored mental models.

## Scope
- Detects overconfidence, staleness, unsafe content and supersession in mental model history.

## Current State
- Operational. Created by Pack 5.2.2.

## Physical Evidence
- `layers/l2_brain/flat_brain/mental_model_truth_hygiene.py`
- `.aiwg/reports/mental_model_truth_hygiene_latest.json`
- `.aiwg/mental_models/runtime_model_quarantine.json`

## Contract Invariants
- never deletes models
- quarantines quality_score 100 with Kuzu DEGRADED
- marks empty-relations complex models as needs_review

## Verification
```bash
pytest layers/l2_brain/tests/test_mental_model_truth_hygiene.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5_2_2 Module 1
