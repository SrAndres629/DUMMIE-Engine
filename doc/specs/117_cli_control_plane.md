---
spec_id: "DE-V2-L2-117"
title: "CLI Control Plane"
status: "DEPRECATED"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 117 - CLI Control Plane

## Purpose
Provide a practical control surface to query and operate the runtime artifacts from P10-P21.

## Scope
Covers deterministic command execution, safe missing-artifact handling, JSON output, and evidence reporting.

## Runtime Behavior
Supported commands: `status`, `health`, `latest-context`, `latest-frame`, `cache-summary`, `restart-gate`, `benchmark`, `flywheel`, `next-action`, `compress-context`, `dashboard-data`.

## Inputs
Latest artifacts under `.aiwg/reports/` plus canonical phase state files.

## Outputs
- `.aiwg/reports/cli_control_plane_latest.json`

## Safety Rules
No raw repo dump operations; no secrets/private reasoning acceptance; missing optional artifacts must warn, not crash.

## Missing Artifact Behavior
Missing latest files return `PASS_WITH_WARNINGS` with explicit warning entries.

## Relationship to P10-P17
Consumes context quant, prompt frame, cache summary, restart gate, benchmark, and flywheel outputs.

## Current State

## Physical Evidence
- `.aiwg/reports/cli_control_plane_latest.json`
- `layers/l2_brain/tests/test_cli_control_plane.py`

## Contract Invariants
- Command result includes `decision`, `warnings`, `evidence_refs`.
- Commands are deterministic for fixed local artifacts.
- `compress-context` writes compression latest output.

## Tests Expected
`test_cli_control_plane.py` and control-surface integration tests must pass.

## Verification
```bash
git diff --check
pytest -q layers/l2_brain/tests/test_cli_control_plane.py
```

## Traceability
Upstream: P10-P17 runtime outputs. Downstream: P22 embedding-adapter control surface entrypoint.
