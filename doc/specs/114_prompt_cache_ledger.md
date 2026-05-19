---
spec_id: "DE-V2-L2-114"
title: "PromptCacheLedger"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 114 - PromptCacheLedger

## Purpose
Define append-only prompt frame cache ledger behavior, reusable frame lookup, invalidation rules, and cache summary metrics.

## Scope
Covers JSONL persistence, idempotent writes, invalidation triggers, and reusable-frame selection.

## Why This Exists
Prompt frames should not be rebuilt unnecessarily. P14 cache ledger reduces repeated context assembly cost.

## Current State
Implemented as `layers/l2_brain/flat_brain/prompt_cache_ledger.py` with summary output `.aiwg/reports/prompt_cache_summary_latest.json`.

## Physical Evidence
- `layers/l2_brain/flat_brain/prompt_cache_ledger.py`
- `.aiwg/prompt_cache/prompt_cache_ledger.jsonl`
- `.aiwg/reports/prompt_cache_summary_latest.json`

## Contract Invariants
- Ledger writes are append-only and idempotent by `frame_id`.
- Reuse is denied on source-hash, phase, freshness, receipt, or stale-report mismatch.
- Cache summary reports hit ratio and estimated token savings.

## Verification
```bash
git diff --check
python3 scripts/validate_specs_docs.py || true
pytest -q layers/l2_brain/tests/test_prompt_cache_ledger.py
```

## Traceability
- Upstream: prompt frames from Spec 113
- Downstream: restart gate, benchmark, evolution flywheel
