---
spec_id: "DE-V2-L2-113"
title: "PromptFrameBuilder"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 113 - PromptFrameBuilder

## Purpose
Define prompt frame construction from quantized context with safety gates, stable hashes, and receipt linkage.

## Scope
Covers frame assembly fields, context reference filtering, staleness warning propagation, and source-hash determinism.

## Why This Exists
P10-P13 delivered quantized context. P14 turns that output into model-ready frame inputs without raw repository dumping.

## Current State
Implemented as `layers/l2_brain/prompt_frame_builder.py` with runtime output `.aiwg/reports/prompt_frame_latest.json`.

## Physical Evidence
- `layers/l2_brain/prompt_frame_builder.py`
- `.aiwg/reports/prompt_frame_latest.json`
- `.aiwg/reports/context_quant_result_latest.json`
- `.aiwg/reports/context_receipt_latest.json`

## Contract Invariants
- PromptFrame JSON is parseable and stable in shape.
- Raw repository dump references are forbidden.
- Secret/private-reasoning patterns are rejected.
- Frame `source_hash` is deterministic for equivalent inputs.

## Verification
```bash
git diff --check
python3 scripts/validate_specs_docs.py || true
pytest -q layers/l2_brain/tests/test_prompt_frame_builder.py
```

## Traceability
- Upstream: `context_quant_runtime`, `context_package`, `stale_memory_detector`
- Downstream: `prompt_cache_ledger`, restart gate, benchmark, flywheel
