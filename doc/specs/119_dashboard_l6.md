---
spec_id: "DE-V2-L2-119"
title: "Dashboard L6"
status: "ACTIVE"
layer: "L6"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 119 - Dashboard L6

## Purpose
Render a static L6 dashboard view for runtime control artifacts without external dependencies.

## Scope
Covers dashboard state model and static HTML rendering of runtime health and progression signals.

## Runtime Behavior
Builds `DashboardState` and renders `.html` + `.json` artifacts using local data only.

## Inputs
Current position, next seed, restart gate latest, flywheel latest, benchmark latest, prompt cache summary, stale memory report, prompt frame ref.

## Outputs
- `.aiwg/reports/dashboard_l6_latest.json`
- `.aiwg/reports/dashboard_l6_latest.html`

## Safety Rules
No browser launch, no HTTP server, no external frontend frameworks.

## Missing Artifact Behavior
Missing source files become warnings inside dashboard state.

## Relationship to P10-P17
Displays governance/runtime outputs from context quant, frame/cache, gate/benchmark/flywheel chain.

## Current State
Implemented in `layers/l6_skin/dashboard_renderer.py`.

## Physical Evidence
- `layers/l6_skin/dashboard_renderer.py`
- `.aiwg/reports/dashboard_l6_latest.json`
- `.aiwg/reports/dashboard_l6_latest.html`

## Contract Invariants
- HTML is deterministic and standalone.
- JSON state includes current/next phase and flywheel decision.

## Tests Expected
`layers/l6_skin/tests/test_dashboard_renderer.py` and integration tests pass.

## Verification
```bash
git diff --check
pytest -q layers/l6_skin/tests/test_dashboard_renderer.py
```

## Traceability
Upstream: process monitor + runtime latest artifacts. Downstream: P22+ operator visibility.
