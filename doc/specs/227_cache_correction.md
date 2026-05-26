---
status: SUPERSEDED
claims:
- id: correction_param
  description: Parametro correction= aceptado en dummie_process
  severity: critical
- id: reject_mode_learning
  description: Modo reject almacena correcciones en cache
  severity: high
implementations:
- file: layers/l1_nervous/semantic_cache.py
  class: SemanticRouteCache
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Cache Correction — Learning From Routing Mistakes

**Date:** 2026-05-26
**Phase:** G5
**Requires reboot:** No
**Depends on:** Nothing
**Files modified:** `layers/l1_nervous/semantic_cache.py`, `layers/l1_nervous/tools.py` (dummie_process)

## Problem

The semantic route cache is write-once. When a route is wrong (e.g., domain classified as "code" but should be "filesystem"), the bad route is re-served on every subsequent identical intent. The agent has no way to correct it. The only remedy is waiting for TTL expiry.

## Design

### Two new methods on SemanticRouteCache

**1. invalidate(query) — remove wrong entry**

```python
async def invalidate(self, query: str) -> bool:
    """Remove a cached entry. Returns True if found and removed."""
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    async with self._lock:
        if query_hash in self._l1:
            idx = self._l1.pop(query_hash)
            self._entries[idx] = self._entries[-1]  # swap with last
            self._embeddings[idx] = self._embeddings[-1]
            self._entries.pop()
            self._embeddings = self._embeddings[:-1]  # resize
            logger.info("cache invalidated: %s", query[:50])
            return True
    return False
```

**2. correct(query, new_result) — replace with corrected route**

```python
async def correct(self, query: str, new_result: dict) -> None:
    """Store a corrected route with extended TTL."""
    # Invalidate old entry first
    await self.invalidate(query)
    
    # Store corrected entry with 10x TTL
    async with self._lock:
        entry = CacheEntry(
            query=query,
            result=new_result,
            timestamp=time.monotonic(),
            ttl=3000,  # 50 minutes for corrected routes
            hit_count=1,
        )
        # Embed and store (reuse existing set logic)
        entry.embedding = await self._embed(query)
        idx = len(self._entries)
        self._l1[query_hash] = idx
        self._entries.append(entry)
        self._embeddings = np.vstack([self._embeddings, entry.embedding[None, :]])
    
    logger.info("cache corrected: %s", query[:50])
```

**3. get_stats() enhanced — track corrections**

```python
async def get_stats(self) -> dict:
    return {
        "total_entries": len(self._entries),
        "total_hits": self._total_hits,
        "total_corrections": self._total_corrections,  # NEW
        "correction_rate": round(
            self._total_corrections / max(self._total_hits, 1), 3
        ),
    }
```

### Integration in dummie_process

**New mode: "correct"**

```python
@mcp.tool()
async def dummie_process(intent: str, mode: str = "auto", 
                         correct_gateway: str = None, 
                         correct_server: str = None,
                         correct_tool: str = None) -> str:
    """
    ...
    mode: "correct" — invalidate cached route and store corrected one.
           Requires: correct_gateway or correct_server.
    """
    
    if mode == "correct":
        try:
            from semantic_cache import SemanticRouteCache
            cache = SemanticRouteCache()
            
            correction = {
                "match": True,
                "domain": correct_gateway,
                "servers": [correct_server] if correct_server else [],
                "tools": [{"server": correct_server, "tool": correct_tool}] if correct_tool else [],
                "confidence": 1.0,
                "strategy": "manual_correction",
                "corrected_at": time.time(),
            }
            await cache.correct(intent, correction)
            return json.dumps({
                "corrected": True,
                "intent": intent,
                "new_route": correction,
            })
        except Exception as e:
            return json.dumps({"corrected": False, "error": str(e)})
    
    # ... rest of existing flow ...
```

### Automatic correction detection

When the agent calls `dummie_process(intent=X, mode="execute")` and then immediately calls a DIFFERENT tool directly, the gateway can detect the correction:

```python
# In dummie_execute_capability (old tool, if still exposed):
# If the previous dummie_process call's route was for server A but
# the agent is now calling server B for the same intent pattern,
# auto-correct the cache.

# This is optional and can be added later.
```

## Success criteria

| Metric | Before | After |
|--------|--------|-------|
| Wrong route TTL | Full TTL (300s) | Invalidated immediately |
| Corrected route TTL | N/A | 3000s (10x normal) |
| Correction feedback | Not possible | `mode="correct"` |
| Correction tracking | None | `get_stats()` includes corrections |
| Agent can fix bad routes | No | Yes |