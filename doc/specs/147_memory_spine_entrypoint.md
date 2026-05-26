---
spec_id: 147_memory_spine_entrypoint
title: 147 Memory Spine Entrypoint
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_3
last_verified_on: '2026-05-16'
claims:
- id: 147_memory_spine_entrypoint-file-valid
  description: Spec file '147_memory_spine_entrypoint.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/147_memory_spine_entrypoint.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 147: Memory Spine Entrypoint

## Purpose
Provide causal memory retrieval before every sovereign interaction, falling back to file-backed memory when Kuzu is unavailable.

## Scope
- Queries learning episodes, vault entries, and report-based memory for intent-relevant context.
- Reports DEGRADED_WITH_FILE_BACKED_MEMORY when Kuzu unavailable.
- Never exposes private chain-of-thought.

## Runtime Behavior
1. Check Kuzu status via memory_spine_sync_latest.json.
2. Scan session store learning episodes for keyword matches.
3. Scan vault entries for relevant context.
4. Scan key reports for relevant references.
5. Return MemorySpineRetrievalResult with decision, refs, and warnings.

## Safety Rules
- Must not expose private reasoning or chain-of-thought.
- Must not write to Kuzu or modify any persistent state beyond its own report.
- Must function even if SessionStore import fails.

## Current State
- Operational with file-backed fallback. Kuzu is DEGRADED.

## Physical Evidence
- `layers/l2_brain/memory/memory_spine_entrypoint.py`
- `.aiwg/reports/memory_spine_entrypoint_latest.json`
- `.aiwg/schemas/memory_spine_entrypoint.schema.json`

## Contract Invariants
- If Kuzu DEGRADED → status must be DEGRADED_WITH_FILE_BACKED_MEMORY.
- Must always set `used_before_chat_response: true`.
- Must never expose private reasoning data.

## Verification
```bash
python3 layers/l2_brain/memory/memory_spine_entrypoint.py "what should I do next?"
python3 -m pytest layers/l2_brain/tests/test_memory_spine_entrypoint.py -q
```

## Traceability
- Implements POST_PLAN_V1_OPERATIONALIZATION_PACK_3 Module 2.
- Consumed by `dummie_chat_cli.py` before every response.
