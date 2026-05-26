---
spec_id: DE-V2-L2-114
title: PromptCacheLedger
status: DEPRECATED
layer: L2
last_verified_on: '2026-05-16'
version: 1.0.0
namespace: dummie.engine.plan_v1
claims:
- id: 114_prompt_cache_ledger-file-valid
  description: Spec file '114_prompt_cache_ledger.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/114_prompt_cache_ledger.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 114 - PromptCacheLedger

## Purpose
Define append-only prompt frame cache ledger behavior, reusable frame lookup, invalidation rules, and cache summary metrics.

## Scope
Covers JSONL persistence, idempotent writes, invalidation triggers, and reusable-frame selection.

## Why This Exists
Prompt frames should not be rebuilt unnecessarily. P14 cache ledger reduces repeated context assembly cost.

## Current State

## Physical Evidence
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
