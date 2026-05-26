---
status: SUPERSEDED
claims:
- id: cache_wired_to_discover
  description: SemanticRouteCache usado en dummie_discover_capabilities
  severity: critical
- id: no_import_errors
  description: SMART components importables sin errores
  severity: high
implementations:
- file: layers/l1_nervous/tools.py
  function: dummie_discover_capabilities
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Connect SMART MetaGateway to Tool Handlers

**Date:** 2026-05-26  
**Phase:** B  
**Requires reboot:** No  
**Depends on:** Phase A (benchmark)  
**Files created:** None  
**Files modified:** `layers/l1_nervous/tools.py`

## 1. Purpose

Wire the existing SMART MetaGateway components (SemanticRouteCache, SmartRouter) into the actual MCP tool handler `dummie_discover_capabilities`. Currently this handler calls MetacognitiveReasoner.analyze() → LocalLLMBridge → gemma4:e2b (2-10s) for EVERY query with no caching. After this phase, it checks cache first, uses tiny router for classification, and only falls back to LLM when needed.

## 2. What changes

### 2.1 Current flow (no change to legacy path)

```
dummie_discover_capabilities(query)
  → MetacognitiveReasoner.analyze()
    → IntentRouter → exact match? return
    → LocalLLMBridge.reason()  ← gemma4:e2b, 2-10s
    → SmartResearchEngine.search() ← GitHub
```

The `MetacognitiveReasoner` and `LocalLLMBridge` are large classes with complex initialization. We do NOT modify them. We add a **cache-first layer** before them.

### 2.2 New flow (additive, no deletions)

```
dummie_discover_capabilities(query)
  │
  ├─► [NEW] Cache check
  │     ├─ hit → return cached result (skip LLM entirely)
  │     └─ miss → continue
  │
  ├─► [NEW] Smart router classification (if not exact match)
  │     ├─ confidence ≥ 0.8 → add route metadata, continue to LLM
  │     └─ confidence < 0.8 → continue (no change)
  │
  ├─► MetacognitiveReasoner.analyze()  ← unchanged
  │
  └─► [NEW] Cache result (async, non-blocking)
```

**Key principle:** The MetacognitiveReasoner path is NEVER removed or modified. We just add a faster path before it. If cache or router fails, the original code runs exactly as before.

### 2.3 Code change in tools.py

```python
@mcp.tool()
async def dummie_discover_capabilities(query: str = "") -> str:
    _, proxy_manager = setup_internal()

    # [PHASE B] SMART cache check
    if query:
        try:
            from semantic_cache import SemanticRouteCache
            cache = SemanticRouteCache()
            cached = await cache.get(query)
            if cached:
                logger.debug(f"SMART cache HIT for query: {query[:50]}")
                return json.dumps(cached, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"SMART cache check failed (benign): {e}")

    # ... existing code continues unchanged ...
    if hasattr(proxy_manager, "_load_config"):
        proxy_manager._load_config()

    index = CapabilityIndex()
    # ... (full existing path preserved)

    # [PHASE B] Add routing metadata from SmartRouter (if available)
    route_meta = None
    if query:
        try:
            from smart_router import SmartRouter
            router = SmartRouter()
            from context_budget_tools import ContextBudgetRouter
            budget = ContextBudgetRouter()
            tools = budget.get_tools_for_budget(4096)
            route = await router.route(query, tools)
            if route.get("match") and route.get("confidence", 0) >= 0.8:
                route_meta = route
        except Exception:
            pass

    # ... MetacognitiveReasoner.analyze() unchanged ...
    reasoner = MetacognitiveReasoner()
    result = reasoner.analyze(query, index)
    # ... rest of existing output formatting ...

    # [PHASE B] Cache the result (async, non-blocking)
    if query and result.found:
        try:
            from semantic_cache import SemanticRouteCache
            cache = SemanticRouteCache()
            asyncio.create_task(cache.set(query, {
                "query": query,
                "match": result.match,
                "domain": result.intent.domain if result.intent else None,
                "confidence": result.intent.confidence if result.intent else 0.0,
                "route": route_meta,
                "latency_ms": result.latency_ms,
            }))
        except Exception:
            pass

    return "\n".join(output)
```

## 3. Edge cases

| Case | Behavior |
|------|----------|
| Cache unavailable (import error) | Silently continue to original path |
| SmartRouter unavailable (model not loaded) | Silently continue |
| Cache returns stale result | TTL handles expiry (default 300s) |
| Query is empty string | No cache check, no routing (original behavior) |
| Concurrent requests | asyncio.Lock in SemanticRouteCache handles writes |
| Cache set fails | Async task, exception caught silently |

## 4. Success criteria

| Metric | Before | After (target) |
|--------|--------|----------------|
| Cache hit adds to discover latency | N/A | <1ms |
| Cache miss adds to discover latency | N/A | <5ms (router check) |
| Cache hit rate (repeated queries) | 0% | 100% |
| P50 discover latency (cached queries) | 2-10s | <50ms |
| Error rate increase | 0% | 0% (catch-all exceptions) |

## 5. Files

| File | Action |
|------|--------|
| `layers/l1_nervous/tools.py` | **Modify** — add cache check + cache write in dummie_discover_capabilities |
| `.aiwg/benchmarks/post-phase-b_*.json` | **Create** — re-run benchmark |

## 6. Verification

1. `uv run python -m tests.bench_metagateway` — re-run baseline
2. `uv run python -m tests.test_smart_components` — 38 tests still pass
3. Manual: call `dummie_discover_capabilities(query="find file")` twice — second should be instant