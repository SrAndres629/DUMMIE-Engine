---
spec_id: "173_context_packet_optimizer"
title: "Context Packet Optimizer"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the context packet optimizer (HEARTBEAT-2) to analyze different strategies for context packing and select the most token-efficient approach that preserves active evidence.

## Current State
Under implementation. Will process raw context packages and compare compaction options to output structured logs conforming to `context_packet_optimization.schema.json`.

## Physical Evidence
- Test suite: `layers/l2_brain/tests/test_context_packet_optimizer.py`
- JSON Schema: `.aiwg/schemas/context_packet_optimization.schema.json`
- Output reports: `.aiwg/reports/context_packet_optimization_latest.json` and `.aiwg/reports/context_packet_optimization_latest.md`

## Contract Invariants
- **Token Reduction**: The selected strategy must result in a `reduction_ratio` greater than 1.0 compared to the raw scan context estimate.
- **Evidence Preservation**: The chosen strategy must not discard required evidence files.
- **Strategy Comparison**: Compares multiple options such as `raw_scan_context`, `wiring_matrix_only`, `shadow_classification_only`, and `6d_context_packet`.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_context_packet_optimizer.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `context_packet_optimization.schema.json`
