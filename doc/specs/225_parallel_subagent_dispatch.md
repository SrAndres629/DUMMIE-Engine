---
status: SUPERSEDED
claims:
- id: subagent_splitters
  description: Splitters multi-agente definidos
  severity: high
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Parallel Sub-intent Dispatch

**Date:** 2026-05-26
**Phase:** G3
**Requires reboot:** No
**Depends on:** Nothing
**Files modified:** `layers/l1_nervous/tools.py` (dummie_process)

## Problem

Compound queries force sequential execution. When the agent asks "search for auth in Python files AND check git history for auth.py", it must either:
- Make 2 separate `dummie_process` calls (2 round-trips)
- Route through a single tool that handles both (unlikely if different domains)

Both approaches waste time and context.

## Design

### Parallel intent detection

Simple conjunction-based split, no NLP needed:

```python
PARALLEL_SEPARATORS = [
    (r"\s+AND\s+", "AND"),
    (r"\s+y\s+", "y"),           # Spanish "and"
    (r"\s+also\s+", "also"),
    (r"\s+además\s+", "además"),
    (r";\s*", ";"),
]

def _split_parallel_intents(intent: str) -> list[str]:
    """Detect and split compound intents by conjunction."""
    for pattern, sep in PARALLEL_SEPARATORS:
        parts = re.split(pattern, intent, maxsplit=1)
        if len(parts) >= 2 and all(len(p.strip()) > 10 for p in parts):
            return [p.strip() for p in parts]
    return [intent]  # No split detected
```

### Parallel execution in dummie_process

```python
@mcp.tool()
async def dummie_process(intent: str, mode: str = "auto") -> str:
    # ... existing cache check ...

    # Detect compound intents
    sub_intents = _split_parallel_intents(intent)
    
    if len(sub_intents) > 1:
        # Parallel execution of sub-intents
        tasks = [_process_single(sub, mode) for sub in sub_intents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        response = {
            "intent": intent,
            "parallel": True,
            "sub_intents": len(sub_intents),
            "results": [
                r if not isinstance(r, Exception) else {"error": str(r)}
                for r in results
            ],
            "total_latency_ms": ...
        }
        return json.dumps(response, indent=2)
    
    # Single intent (original flow)
    return await _process_single(intent, mode)
```

### _process_single — extracted internal function

The existing dummie_process body (cache → router → skill → execute) becomes `_process_single`, reusable for both single and parallel paths:

```python
async def _process_single(intent: str, mode: str) -> dict:
    """Internal: process a single intent through the full pipeline."""
    # ... existing pipeline logic (cache check, router, skill, execute) ...
    return response
```

## Constraints

| Rule | Why |
|------|-----|
| Sub-intent must have >10 chars after trimming | Prevents false splits on "X and Y" where X or Y is a single word |
| Max 3 parallel sub-intents | Context budget consideration — don't overwhelm |
| Each sub-intent gets its own cache check | Cache may hit on one but miss on another |
| Errors in one sub-intent don't abort others | `return_exceptions=True` in gather |

## Success criteria

| Metric | Before | After |
|--------|--------|-------|
| Compound "X AND Y" | 2 sequential calls | 1 call, internal parallelism |
| Latency for compound queries | T1 + T2 (sequential) | max(T1, T2) (parallel) |
| Sub-intent isolation | N/A | Errors don't cascade |