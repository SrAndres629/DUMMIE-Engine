---
spec_id: "177_polyglot_probe_orchestrator"
title: "Polyglot Probe Orchestrator"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the polyglot probe orchestrator (HEARTBEAT-2) to detect and catalog first-party workspace source assets across multiple languages (Python, Go, Elixir, Rust, TS/JS, etc.) without dependencies/venv scanning or heavy execution workloads.

## Current State
Under implementation. Will parse workspace configurations and write outputs conforming to `polyglot_probe.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/polyglot_probe_orchestrator.py`
- Test suite: `layers/l2_brain/tests/test_polyglot_probe_orchestrator.py`
- JSON Schema: `.aiwg/schemas/polyglot_probe.schema.json`
- Output reports: `.aiwg/reports/polyglot_probe_latest.json` and `.aiwg/reports/polyglot_probe_latest.md`

## Contract Invariants
- **Multi-language Audit**: Safely scans manifests (mix.exs, go.mod, Cargo.toml, package.json, requirements.txt) and counts source files.
- **Dependency Exclusion**: Must completely respect build cache and dependency directories (e.g. `node_modules`, `.venv`, `target`, `_build`).
- **Safety**: No compiling, transpiling, mix tasks, npm scripts, or builds can be spawned.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_polyglot_probe_orchestrator.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `polyglot_probe.schema.json`
