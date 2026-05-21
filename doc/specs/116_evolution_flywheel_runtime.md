---
spec_id: "DE-V2-L2-116"
title: "EvolutionFlywheelRuntime"
status: "DEPRECATED"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 116 - EvolutionFlywheelRuntime

## Purpose
Define evidence-based runtime decisioning for whether DUMMIE should continue, repair, refresh, rerun benchmark, or block progression.

## Scope
Covers signal ingestion from restart gate, benchmark, cache summary, stale memory report, and phase-state files.

## Why This Exists
P17 introduces flywheel control so phase progression depends on runtime evidence instead of narrative optimism.

## Current State

## Physical Evidence
- `.aiwg/reports/evolution_flywheel_latest.json`
- `.aiwg/reports/restart_integration_gate_latest.json`
- `.aiwg/reports/context_efficiency_benchmark_latest.json`

## Contract Invariants
- Decision must be one of the allowed operational actions.
- Output always includes blocking reasons, expected gains, confidence, and required next tests.
- Runtime failure signals must dominate optimistic advancement.

## Verification
```bash
git diff --check
python3 scripts/validate_specs_docs.py || true
pytest -q layers/l2_brain/tests/test_evolution_flywheel_runtime.py
```

## Traceability
- Upstream: restart gate + context efficiency benchmark + cache summary
- Downstream: P18 CLI Control Plane prioritization
