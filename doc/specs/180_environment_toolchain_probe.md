---
spec_id: "180_environment_toolchain_probe"
title: "Environment Toolchain Probe"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the environment toolchain probe (HEARTBEAT-2.1) to audit the host políglota compilers, interpreters, and package managers safely via command version queries.

## Current State
Under implementation. Will safely run subprocess version queries and compile structured results conforming to `environment_toolchain_probe.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/environment_toolchain_probe.py`
- Test suite: `layers/l2_brain/tests/test_environment_toolchain_probe.py`
- JSON Schema: `.aiwg/schemas/environment_toolchain_probe.schema.json`
- Output reports: `.aiwg/reports/environment_toolchain_probe_latest.json` and `.aiwg/reports/environment_toolchain_probe_latest.md`

## Contract Invariants
- **Non-Destructive Operations**: Probes must NEVER spawn background compilers, execute large compiles, install packages, or mutate local settings.
- **Fail-Safe Robustness**: If a toolchain (e.g. `go`, `rustc`, `elixir`, `node`) is missing on the host, the probe must gracefully record it as missing without crashing.
- **Lightweight queries**: Commands run must be limited strictly to `--version` or `version` commands with short timeout limits.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_environment_toolchain_probe.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.1)
- Contract Schema: `environment_toolchain_probe.schema.json`
