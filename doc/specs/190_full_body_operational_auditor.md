---
spec_id: "190_full_body_operational_auditor"
title: "Full Body Operational Auditor"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
Map and audit the physical existence, connection, and readiness score of every DUMMIE Engine "organ" into a unified operational dashboard to evaluate structural cohesion.

## Current State
Under implementation.

## Physical Evidence
- Core module: `layers/l2_brain/full_body_operational_auditor.py`
- Test suite: `layers/l2_brain/tests/test_full_body_operational_auditor.py`
- JSON Schema: `.aiwg/schemas/full_body_operational_audit.schema.json`
- Output reports: `.aiwg/reports/full_body_operational_audit_latest.json` and `.aiwg/reports/full_body_operational_audit_latest.md`

## Contract Invariants
- **Whole-Body Classifications**: Minimum tracked organs include: eyes (scanners, matrix), brain (models, gates), memory (session, episodes, graph), nervous system (heartbeat, ledger), metabolism (budget, tokens), mouth (CLI), hands (gateway, daemon), immune system (hygiene, safety gates).
- **Integrity Score Calibration**: Overall body score must reflect fallback and degraded states accurately.
- **Accurate Wire Classification**: Unwired and shadow organs must be classified.

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_full_body_operational_auditor.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `full_body_operational_audit.schema.json`
