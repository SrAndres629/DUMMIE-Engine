---
spec_id: "179_degraded_capability_registry"
title: "Degraded Capability Registry"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the degraded capability registry (HEARTBEAT-2.1) to serve as the unified source of truth for the actual runtime status of DUMMIE's primary engines.

## Current State
Under implementation. Will ingest dependency, preflight, and calibration reports, mapping capabilities conforming to `degraded_capability_registry.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/degraded_capability_registry.py`
- Test suite: `layers/l2_brain/tests/test_degraded_capability_registry.py`
- JSON Schema: `.aiwg/schemas/degraded_capability_registry.schema.json`
- Output reports: `.aiwg/reports/degraded_capability_registry_latest.json` and `.aiwg/reports/degraded_capability_registry_latest.md`

## Contract Invariants
- **Completeness**: The registry MUST evaluate at minimum: `kuzu_4dtes_persistence`, `real_semantic_embeddings`, `daemon_persistent_runtime`, `gateway_live_dispatch`, `polyglot_build_test_runtime`, and `token_usage_measurement`.
- **Honest Mapping**: Claimed readiness (e.g. 100%) must be penalty-adjusted or downgraded based on actual import/toolchain diagnostic checks.
- **Traceability**: Every registered capability must refer to its verification findings and evidence reports.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_degraded_capability_registry.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.1)
- Contract Schema: `degraded_capability_registry.schema.json`
