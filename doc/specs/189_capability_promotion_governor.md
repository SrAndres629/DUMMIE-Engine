---
spec_id: "189_capability_promotion_governor"
title: "Capability Promotion Governor"
status: "DEPRECATED"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
Enforce rigorous, evidence-backed gates for promoting any DUMMIE capability state. Prevent false `READY` claims unless the capability has passed physical verification, integration paths, and tests.

## Current State
Under implementation.

## Physical Evidence
- Test suite: `layers/l2_brain/tests/test_capability_promotion_governor.py`
- JSON Schema: `.aiwg/schemas/capability_promotion_governor.schema.json`
- Output reports: `.aiwg/reports/capability_promotion_governor_latest.json` and `.aiwg/reports/capability_promotion_governor_latest.md`

## Contract Invariants
- **Gate Integrity**: Promotion to `READY` strictly requires runtime operation, integration path, unit/integration tests, and heartbeat consumption.
- **Safety Fallback**: If physical runtime proof exists but full integration is incomplete, recommend `READY_CANDIDATE` or `SANDBOX_READY`.
- **Zero Ambition Policy**: Do not allow promotion based on developer intent or simple package presence.

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_capability_promotion_governor.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `capability_promotion_governor.schema.json`
