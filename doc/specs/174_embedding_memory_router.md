---
spec_id: "174_embedding_memory_router"
title: "Embedding Memory Router"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the embedding memory router (HEARTBEAT-2) to safely index high-value context items and provide a local search/retrieval mechanism.

## Current State
Under implementation. Will process context items and rank search queries using a deterministic fallback vector scheme conforming to `embedding_memory_router.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/embedding_memory_router.py`
- Test suite: `layers/l2_brain/tests/test_embedding_memory_router.py`
- JSON Schema: `.aiwg/schemas/embedding_memory_router.schema.json`
- Output reports: `.aiwg/reports/embedding_memory_router_latest.json` and `.aiwg/reports/embedding_memory_router_latest.md`

## Contract Invariants
- **Deterministic Offline Fallback**: Under local security limits, must fall back to a deterministic model (`DETERMINISTIC_FALLBACK` or `PROVIDER_DISABLED`) and issue appropriate warnings.
- **API Guard**: Must never make network calls or require API keys.
- **Surgical Indexing**: Indexes only the high-value 6D context items rather than loading the entire codebase.

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_embedding_memory_router.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `embedding_memory_router.schema.json`
