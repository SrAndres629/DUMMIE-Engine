---
spec_id: "159_cognitive_bias_detector"
title: "159 Cognitive Bias Detector"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 159: Cognitive Bias Detector

## Purpose
Flags overconfidence and report optimism.

## Scope
- Evaluates reasoning results against physical reality metrics.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/cognition/cognitive_bias_detector.py`
- `.aiwg/reports/cognitive_bias_report_latest.json`
- `.aiwg/schemas/cognitive_bias_report.schema.json`

## Contract Invariants
- flags quality_score 100 with degraded integrations
- flags scaling intents with Kuzu degraded

## Verification
```bash
python3 layers/l2_brain/cognition/cognitive_bias_detector.py
pytest layers/l2_brain/tests/test_cognitive_bias_detector.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5_2 Module 4
