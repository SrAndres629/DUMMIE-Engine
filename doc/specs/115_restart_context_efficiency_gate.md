---
spec_id: "DE-V2-L2-115"
title: "RestartIntegrationGate + ContextEfficiencyBenchmark"
status: "DEPRECATED"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 115 - RestartIntegrationGate + ContextEfficiencyBenchmark

## Purpose
Define restart survivability checks and context efficiency benchmark comparisons before continuing phase execution.

## Scope
Covers critical-state validation, runtime-module import checks, and three-strategy context efficiency estimates.

## Why This Exists
P15/P16 must prove runtime can recover after restart and that context optimization offers measurable value.

## Current State
Implemented as `restart_integration_gate.py` and `context_efficiency_benchmark.py` with `latest` reports.

## Physical Evidence
- `.aiwg/reports/restart_integration_gate_latest.json`
- `.aiwg/reports/context_efficiency_benchmark_latest.json`

## Contract Invariants
- Restart gate fails on invalid critical state or missing critical imports.
- Optional missing artifacts are warnings, not implicit pass.
- Benchmark must always compare `raw_naive_estimate`, `folder_notes_only`, and `quantized_context_frame`.
- Quantized strategy cannot claim better efficiency if required context is lost.

## Verification
```bash
git diff --check
python3 scripts/validate_specs_docs.py || true
pytest -q \
  layers/l2_brain/tests/test_restart_integration_gate.py \
  layers/l2_brain/tests/test_context_efficiency_benchmark.py
```

## Traceability
- Upstream: specs 113/114 outputs and P10-P13 artifacts
- Downstream: evolution flywheel phase decisioning
