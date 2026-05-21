---
spec_id: "178_runtime_dependency_auditor"
title: "Runtime Dependency Auditor"
status: "DEPRECATED"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the runtime dependency auditor (HEARTBEAT-2.1) to diagnose the physical presence of python packages, configuration boundaries, and capabilities, distinguishing between real, simulated, fallback, and dry-run modes.

## Current State
Under implementation. Will process python imports, read project manifest structures, and compile validated results conforming to `runtime_dependency_audit.schema.json`.

## Physical Evidence
- Test suite: `layers/l2_brain/tests/test_runtime_dependency_auditor.py`
- JSON Schema: `.aiwg/schemas/runtime_dependency_audit.schema.json`
- Output reports: `.aiwg/reports/runtime_dependency_audit_latest.json` and `.aiwg/reports/runtime_dependency_audit_latest.md`

## Contract Invariants
- **Non-Destructive Execution**: The auditor must NEVER invoke pip install, modify environment variables destructively, or write self-mutations.
- **Degraded Mapping**: If the `kuzu` package is missing or fails to import, the capability must be flagged as `DEGRADED` or `MISSING`.
- **Embedding Falling back**: If the embedding provider is deterministically mocked, it must be flagged as `FALLBACK`, never `READY`.
- **Validation schema compliance**: Every report generated must pass validation against its JSON Schema contract.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_runtime_dependency_auditor.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.1)
- Contract Schema: `runtime_dependency_audit.schema.json`
