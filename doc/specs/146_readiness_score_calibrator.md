---
spec_id: "146_readiness_score_calibrator"
title: "146 Readiness Score Calibrator"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_3"
last_verified_on: "2026-05-16"
---

# Spec 146: Readiness Score Calibrator

## Purpose
Ensure that system maturity metrics are honest and reflect real physical constraints (e.g. Kuzu DEGRADED, advisory-only capabilities).

## Scope
- Detects overconfident scores when physical infrastructure is degraded.
- Penalizes memory, token, entrypoint, and autonomy scores based on evidence.
- Produces calibrated 0-10 scores for each readiness dimension.

## Runtime Behavior
1. Load latest reports (memory sync, context coverage, chat CLI, token benchmark, capability scorecard).
2. Detect degraded conditions and generate `ReadinessCalibrationFinding` entries.
3. Calculate penalty-adjusted scores per dimension.
4. Write JSON and MD reports.

## Safety Rules
- Report-only. Does not mutate workspace.
- Must not allow perfect score if Kuzu is DEGRADED.
- Must not allow perfect token score if benchmark is missing.

## Current State
- Operational. Detects 6 degradation patterns including advisory/dry-run modes.

## Physical Evidence
- `layers/l2_brain/readiness_score_calibrator.py`
- `.aiwg/reports/readiness_score_calibration_latest.json`
- `.aiwg/schemas/readiness_score_calibration.schema.json`

## Contract Invariants
- If Kuzu DEGRADED → `memory_spine_readiness` < 10.
- If no token benchmark → `token_economy_readiness` < 10.
- If chat CLI lacks memory spine → `entrypoint_sovereignty_readiness` < 10.
- If capabilities advisory-only → `autonomy_readiness` < 10.

## Verification
```bash
python3 layers/l2_brain/readiness_score_calibrator.py
python3 -m pytest layers/l2_brain/tests/test_readiness_score_calibrator.py -q
```

## Traceability
- Implements POST_PLAN_V1_OPERATIONALIZATION_PACK_3 Module 1.
- Consumed by `sovereign_runtime_readiness.py`.
