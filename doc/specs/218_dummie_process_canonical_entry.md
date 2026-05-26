---
status: SUPERSEDED
claims:
- id: dummie_process_registered
  description: dummie_process registrado como tool MCP publica
  severity: critical
- id: full_pipeline_structure
  description: 'Pipeline completo: cache, route, skill, execute, compress, verify'
  severity: critical
implementations:
- file: layers/l1_nervous/tools.py
  function: dummie_process
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# dummie_process — Canonical Entry Point

**Date:** 2026-05-26  
**Phase:** C  
**Requires reboot:** No  
**Depends on:** Phase B (SMART cache wired to handlers)  
**Files created:** None  
**Files modified:** `layers/l1_nervous/tools.py`

## 1. Purpose

Create a single MCP tool `dummie_process` that becomes the canonical entry point for the DUMMIE Engine. It unifies discovery (routing) + execution into one tool, with SMART cache + tiny router + context budget + skill matching all in the pipeline. Existing tools remain functional but this is the primary interface.

## 2. Design

### 2.1 Tool signature

```python
@mcp.tool()
async def dummie_process(intent: str, mode: str = "auto") -> str:
    """
    Process a query through the SMART MetaGateway pipeline.
    
    intent: Query or intent to process.
    mode:
      - "discover": Find the right tool/server, return route info.
      - "execute": Find the tool AND run it against arguments in intent.
      - "auto": Discover first. If unique match with high confidence, auto-execute.
    """
```

### 2.2 Pipeline

```
dummie_process(intent, mode="auto")
  │
  ├─ 1. Cache check (SemanticRouteCache)
  │     hit → return cached result
  │
  ├─ 2. Context budget resolution
  │     → determine available context windows
  │     → select tool tiers (1, 2, or 3)
  │
  ├─ 3. SmartRouter classification
  │     → Qwen3.5:0.8b → domain + confidence
  │     → low confidence (< 0.6) → escalate to step 4
  │     → high confidence → proceed to maybe-execute
  │
  ├─ 4. [Fallback] MetacognitiveReasoner (gemma4:e2b)
  │     → full LLM reasoning for complex queries
  │
  ├─ 5. [if mode=auto|execute] MCPProxyManager.call_tool()
  │     → direct STDIO tool execution
  │
  └─ 6. Cache result (async, non-blocking)
```

### 2.3 Response format

```json
{
  "query": "...",
  "stage": "cache_hit|cache_miss|smart_router|llm_reasoner",
  "routing": {
    "matched": true,
    "domain": "workspace_io",
    "server": "filesystem",
    "tool": "search_files",
    "confidence": 0.85,
    "latency_ms": 42.3
  },
  "execution": {
    "executed": false,
    "result": null,
    "latency_ms": null,
    "error": null
  },
  "context": {
    "tools_available": 45,
    "tools_considered": 15,
    "budget_tier": 2,
    "tokens_saved": 3500
  }
}
```

## 3. Implementation

### 3.1 Code skeleton

```python
@mcp.tool()
async def dummie_process(intent: str, mode: str = "auto") -> str:
    """
    [CANONICAL] Process a query through the SMART MetaGateway pipeline.
    Cache-first routing + optional auto-execution.
    """
    _, proxy_manager = setup_internal()
    t_start = time.monotonic()

    if mode not in ("discover", "execute", "auto"):
        mode = "auto"

    # ── 1. Cache check ──
    try:
        from semantic_cache import SemanticRouteCache
        cache = SemanticRouteCache()
        cached = await cache.get(intent)
        if cached:
            cached["_route_from_cache"] = True
            return json.dumps(cached, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # ── 2. Context budget ──
    try:
        from context_budget_tools import ContextBudgetRouter
        budget = ContextBudgetRouter()
        tools_tier = budget.get_tools_for_budget(8192)
        tier_level = budget._resolve_tier(8192)
    except Exception:
        tools_tier = None
        tier_level = 1

    # ── 3. Capability index ──
    if hasattr(proxy_manager, "_load_config"):
        proxy_manager._load_config()
    local_tools = internal_mcp._tool_manager.list_tools()
    index = await _CAPABILITY_INDEX_CACHE.get_index(local_tools, proxy_manager)

    # ── 4. SmartRouter classification ──
    route_info = None
    try:
        from smart_router import SmartRouter
        router = SmartRouter()
        route = await router.route(intent, tools_tier.get(tier_level, {}))
        if route.get("match") and route.get("confidence", 0) >= 0.8:
            route_info = route
    except Exception:
        pass

    # ── 5. [Fallback] MetacognitiveReasoner ──
    if not route_info:
        reasoner = MetacognitiveReasoner()
        result = reasoner.analyze(intent, index)
        if result.found and result.match:
            route_info = {
                "matched": True,
                "stage": "llm_reasoner",
                "domain": result.intent.domain if result.intent else "unknown",
                "server": result.match.get("id", "").split(".")[0],
                "tool": result.match.get("id", ""),
                "confidence": result.intent.confidence if result.intent else 0.0,
                "latency_ms": result.latency_ms,
            }
        else:
            route_info = {
                "matched": False,
                "stage": "llm_reasoner",
                "message": getattr(result, "message", "No match found"),
                "latency_ms": getattr(result, "latency_ms", 0),
            }

    # ── 6. Execute (if mode allows and match found) ──
    execution = {"executed": False, "result": None, "latency_ms": None, "error": None}
    if route_info.get("matched") and mode in ("execute", "auto"):
        try:
            parts = route_info["tool"].split(".", 1)
            if len(parts) == 2:
                t_exec = time.monotonic()
                exec_result = await proxy_manager.call_tool(
                    parts[0], parts[1], {"intent": intent}
                )
                execution["executed"] = True
                execution["result"] = str(exec_result)[:500]
                execution["latency_ms"] = (time.monotonic() - t_exec) * 1000
        except Exception as e:
            execution["error"] = str(e)

    # ── 7. Build response ──
    response = {
        "intent": intent,
        "mode": mode,
        "routing": route_info,
        "execution": execution,
        "total_latency_ms": (time.monotonic() - t_start) * 1000,
    }

    # ── 8. Cache result ──
    try:
        if route_info.get("matched"):
            from semantic_cache import SemanticRouteCache
            cache2 = SemanticRouteCache()
            asyncio.create_task(cache2.set(intent, response))
    except Exception:
        pass

    return json.dumps(response, indent=2, ensure_ascii=False)
```

### 3.2 Edge cases

| Case | Behavior |
|------|----------|
| Empty intent | Return error message |
| Mode not recognized | Default to "auto" |
| Cache returns stale result | SemanticRouteCache TTL handles expiry |
| SmartRouter unavailable | Falls back to MetacognitiveReasoner |
| MetacognitiveReasoner unavailable | Returns error |
| Execution fails | Route info returned, execution.error populated |
| Tool not found | matched=false, no execution attempted |
| Network timeout in execution | Handled by MCPProxyManager circuit breaker |

## 4. Tests

Add tests to `test_smart_components.py`:

1. `test_process_discover_mode` — mode=discover returns route info only
2. `test_process_auto_mode_high_confidence` — auto-executes with high confidence
3. `test_process_auto_mode_low_confidence` — returns route info only
4. `test_process_cache_hit` — repeated query returns cached
5. `test_process_empty_intent` — handles gracefully
6. `test_process_fallback_to_reasoner` — when SmartRouter fails

## 5. Success criteria

| Metric | Before (Phase B) | After (Phase C) | 
|--------|-----------------|-----------------|
| Agent tools exposed | 8 | 9 (+1 new) |
| Route+execute in one call | No (2 separate calls) | Yes (1 call) |
| Cache coverage | discover only | discover + execute |
| Execution from routing | Manual (agent picks tool) | Automatic (pipeline) |

## 6. Files

| File | Action |
|------|--------|
| `layers/l1_nervous/tools.py` | **Modify** — add dummie_process tool registration |
| `layers/l1_nervous/tests/test_smart_components.py` | **Modify** — add dummie_process tests |