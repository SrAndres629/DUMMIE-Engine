---
spec_id: "148_token_economy_benchmark"
title: "148 Token Economy Benchmark"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_3"
last_verified_on: "2026-05-16"
---

# Spec 148: Token Economy Benchmark

## Purpose
Empirically measure and document the token consumption reduction achieved through surgical context strategies.

## Scope
- Compares at least 5 context strategies from raw to surgical.
- Uses deterministic estimation (no LLM calls).
- Proves that targeted strategies preserve evidence while reducing tokens.

## Runtime Behavior
1. Load repo inventory for baseline file/size counts.
2. Estimate tokens for each strategy using heuristics.
3. Calculate reduction ratio and efficiency score.
4. Write JSON and MD reports.

## Safety Rules
- Report-only. Does not mutate workspace.
- Must not call LLMs or external APIs.
- Measurement must be deterministic and reproducible.

## Current State
- Operational. Uses deterministic_estimate measurement type.

## Physical Evidence
- `layers/l2_brain/flat_brain/token_economy_benchmark.py`
- `.aiwg/reports/token_economy_benchmark_latest.json`
- `.aiwg/schemas/token_economy_benchmark.schema.json`

## Contract Invariants
- Must compare minimum 4 strategies (actually compares 5).
- `raw_folder_naive_estimate` tokens > `repo_intelligence_plus_selected_dossiers` tokens.
- `raw_folder_naive_estimate` tokens > `memory_spine_plus_selected_dossiers` tokens.
- `measurement_type` must be `deterministic_estimate`.

## Verification
```bash
python3 layers/l2_brain/flat_brain/token_economy_benchmark.py
python3 -m pytest layers/l2_brain/tests/test_token_economy_benchmark.py -q
```

## Traceability
- Implements POST_PLAN_V1_OPERATIONALIZATION_PACK_3 Module 3.
- Consumed by readiness calibrator and sovereign runtime readiness.
