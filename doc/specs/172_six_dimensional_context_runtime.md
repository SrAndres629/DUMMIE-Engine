---
spec_id: "172_six_dimensional_context_runtime"
title: "Six-Dimensional Context Runtime"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the six-dimensional context axis runtime (HEARTBEAT-2) to translate raw scan matrices and reports into a curated, high-value, multidimensional context packet.

## Current State
Under implementation. Will process scanner outputs and build structured context packet outputs conforming to `6d_context_packet.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/six_dimensional_context_runtime.py`
- Test suite: `layers/l2_brain/tests/test_six_dimensional_context_runtime.py`
- JSON Schema: `.aiwg/schemas/6d_context_packet.schema.json`
- Output reports: `.aiwg/reports/6d_context_packet_latest.json` and `.aiwg/reports/6d_context_packet_latest.md`

## Contract Invariants
- **Six Axes**: Every packet must evaluate context across all six dimensions: `temporal`, `semantic`, `ontological`, `causal`, `authority_safety`, and `resource`.
- **Evidence Verification**: The decision cannot be `PASS` if `evidence_refs` is empty.
- **Stale Protection**: If the packet includes stale files or reports older than 24 hours, the decision must be `PASS_WITH_WARNINGS`.
- **Budget Compliance**: Packets must estimate input tokens and flag warnings if they exceed context window resource allocations.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_six_dimensional_context_runtime.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `6d_context_packet.schema.json`
