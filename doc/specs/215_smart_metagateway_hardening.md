---
status: SUPERSEDED
claims:
- id: smart_tests_pass
  description: 38 tests unitarios pasan sin errores
  severity: critical
  verify_cmd: uv run python -m pytest tests/test_smart_components.py -q
- id: edge_cases_documented
  description: Edge cases del spec 215 documentados e implementados
  severity: high
implementations:
- file: layers/l1_nervous/semantic_cache.py
  class: SemanticRouteCache
  type: primary
- file: layers/l1_nervous/smart_router.py
  class: SmartRouter
  type: primary
- file: layers/l1_nervous/context_budget_tools.py
  class: ContextBudgetRouter
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# SMART MetaGateway Hardening + Integration Verification

**Date:** 2026-05-26  
**Phase:** 1b (post Phase 0 system tuning, parallel to n8n integration hardening)  
**Requires reboot:** No  

## 1. Purpose

Harden the Phase 1 SMART MetaGateway components (semantic_cache, smart_router, context_budget_tools) and verify they integrate correctly with the n8n agent's gateway modifications. This phase is purely additive — it does NOT modify any gateway, metagateway, routing, or MCP server files that the n8n integration depends on.

## 2. Scope

### 2.1 Files in scope (our Phase 1 components)
- `layers/l1_nervous/semantic_cache.py` — 2-layer semantic route cache
- `layers/l1_nervous/smart_router.py` — Qwen3.5:0.8b router with KV cache
- `layers/l1_nervous/context_budget_tools.py` — 3-tier progressive tool disclosure
- `layers/l1_nervous/metagateway.py` — Already merged with n8n changes (verify only)

### 2.2 Files to verify (n8n agent changes)
- `layers/l1_nervous/capability_index.py` — n8n capabilities added
- `layers/l1_nervous/dummie_sdk/routing/strategies/exact_match.py` — n8n routing rules
- `layers/l1_nervous/mcp_server.py` — n8n MCP server registration
- `layers/l1_nervous/mcp_transport.py` — n8n transport layer
- `layers/l1_nervous/gateway/*.py` — all 5 gateway files for n8n integration
- `dummie_gateway_config.json` — n8n MCP server config

### 2.3 Files NOT in scope (must not touch)
- `dummie_gateway_config.json` — n8n agent's territory
- `layers/l1_nervous/mcp_server.py` — n8n tools registration
- `layers/l1_nervous/mcp_transport.py` — n8n transport
- `layers/l1_nervous/capability_index.py` — n8n capabilities
- `layers/l1_nervous/dummie_sdk/routing/strategies/exact_match.py` — n8n routing
- `layers/l1_nervous/gateway/*.py` — all 5 gateway files
- `layers/l1_nervous/tools.py` — n8n tool registration
- `layers/l2_brain/infrastructure/metagateway_adapter.py` — n8n bridge

## 3. SMART Component Hardening

### 3.1 semantic_cache.py

#### 3.1.1 Thread safety audit
- `asyncio.Lock` exists in `_ensure_lock()` but only used in `set()` — `get()` can read `_l1` and `_entries` concurrently while `set()` modifies them.
- **Fix:** Wrap `get()` writes (L1 hit counter increment, L2 sim check) in lock too, OR use `copy-on-read` pattern.

#### 3.1.2 Edge cases
| Edge case | Current behavior | Required |
|-----------|-----------------|----------|
| Empty cache query | Returns None via L1 miss → early return at L2 | ✅ Correct |
| `max_entries=0` | `_evict_one()` called immediately | Should not set when max_entries=0 |
| `similarity_threshold=1.0` | Only exact L2 matches pass | ✅ Correct (same as L1) |
| Duplicate query within TTL | Overwrites existing entry | ✅ Correct (update in place) |
| Embedding model returns wrong dim | `vstack` raises ValueError | Should validate dim and reject |
| Pickle load with corrupted file | `pickle.load()` raises | Should wrap in try/except and return empty cache |
| Highly concurrent `set()` calls | Lock serializes writes | ✅ Correct (but `get()` reads stale index) |

**Fix for thread safety:** Add lock to `get()` for shared state mutations:
```python
async def get(self, query: str) -> Optional[dict]:
    async with self._lock:
        # ... current logic
```
(This is conservative — the GIL protects dict/append but `_embeddings` numpy reassign breaks atomicity.)

**Fix for embedding dim validation:**
```python
if query_emb.shape[0] != self.embedding_dim:
    logger.warning("Embedding dim mismatch: got %d, expected %d", query_emb.shape[0], self.embedding_dim)
    return None
```

#### 3.1.3 Unit tests
- Test L1 exact hit
- Test L2 semantic hit (mock embedding returns similarity >= threshold)
- Test L2 miss (mock returns similarity < threshold)
- Test empty cache returns None
- Test LRU eviction at max_entries
- Test save/load roundtrip
- Test TTL expiry
- Test concurrent get/set

### 3.2 smart_router.py

#### 3.2.1 Edge cases
| Edge case | Current behavior | Required |
|-----------|-----------------|----------|
| Ollama unavailable | Returns `_empty_result` with error | ✅ Correct |
| Non-JSON output from model | Falls back to embedding | ✅ Correct |
| Empty query string | Sends to Ollama (wastes inference) | Should return fast fail |
| Unknown domain from model | Returns `_empty_result` with error | ✅ Correct |
| Embedding fallback ImportError | Returns None → old path | ✅ Correct |
| High confidence but no tools | Returns domain match without tools | Acceptable (LLM may generate zero tools) |
| Model generates >200 tokens | Truncated by num_predict | ✅ Correct |
| KV cache warmup fails | Warns, retries on first call | ✅ Correct |

**Fix for empty query:**
```python
if not query or not query.strip():
    return self._empty_result(query, error="Empty query")
```

#### 3.2.2 Embedding fallback reliability
The current `_embedding_fallback` tries 2 attempts with different constructors. If both fail, returns None. The caller (`route()`) returns the low-confidence result anyway. This is acceptable but could be misleading — a low-confidence but wrong result is worse than no result.

**Fix:** When embedding fallback succeeds but confidence < 0.3, return the original low-confidence result with a note about fallback failure.

#### 3.2.3 Unit tests
- Test successful routing with mock Ollama response
- Test JSON parsing with markdown fences
- Test JSON parsing with raw JSON
- Test low confidence triggers embedding fallback
- Test embedding fallback returns enriched result
- Test both fallback attempts fail → returns original
- Test empty query → fast fail
- Test DOMAIN_MAP covers all known domains

### 3.3 context_budget_tools.py

#### 3.3.1 Edge cases
| Edge case | Current behavior | Required |
|-----------|-----------------|----------|
| budget=0 | `_resolve_tier(0)` → 0, returns empty dict | Should return tier 1 minimum |
| budget < 500 | returns empty dict | Should return tier 1 (core tools always accessible) |
| Negative budget | returns empty dict | Should clamp to 0 = tier 1 |

**Fix:** Ensure minimum tier 1 tools are always available:
```python
def _resolve_tier(self, budget: int) -> int:
    budget = max(budget, TIER_TOKEN_COST[1])  # clamp to minimum
```

#### 3.3.2 n8n tool coverage
The current tool maps don't include n8n servers. After n8n integration, the tier system should include:
- Tier 1: `n8n` (workflow status, execution lookup — lightweight)
- Tier 2: `n8n_api` (CRUD operations on workflows, credentials)
- Tier 3: `n8n_lint` (diagnostic, workflow quality)

This is a low-priority addition since n8n is still in hardening.

#### 3.3.3 Unit tests
- Test tier resolution for different budgets
- Test tool description formatting
- Test suggest_next_tier with various complexity values
- Test boundary conditions (budget=499, 500, 2000, 5000)

### 3.4 metagateway.py (verify only)

The merged metagateway.py has:
- `use_smart` parameter + env var fallback ✅
- SMART components imported lazily (on demand) ✅
- Graceful fallback on init failure ✅
- `_route_smart` → cache → router → cache write ✅
- `_route_old` preserved verbatim ✅

**Verify:** The lazy import path works:
- When `use_smart=False`: no SMART imports attempted
- When `use_smart=True` but imports fail: logged, falls back to old
- When `use_smart=True` and imports succeed: SMART path active

## 4. n8n Integration Verification

### 4.1 Files to audit for correctness

#### capability_index.py
- Verify n8n capabilities (`n8n`, `n8n_api`, `n8n_lint`) are registered without breaking existing index
- Verify capability_class values match gateway config

#### exact_match.py
- Verify n8n routing patterns don't override existing routes
- Verify n8n patterns use specific triggers (not catch-all regex)

#### mcp_server.py
- Verify n8n tool registration matches the canonical spec topology
- Verify no conflict with existing dummie_* tools

#### Gateway files
- Verify n8n MCP server configs are valid
- Verify port assignments don't conflict

### 4.2 Cross-cutting concerns
| Concern | Check |
|---------|-------|
| Feature flag collision | n8n `DUMMIE_USE_SMART_ROUTING` vs any n8n env vars — no collision expected |
| Import path overlap | SMART components import `dummie_sdk.routing` — n8n modifies same package |
| Config file collision | `dummie_gateway_config.json` shared — verify both SMART metagateway and n8n entries coexist |
| Async event loop | Both systems use asyncio — verify no nested loop conflicts |

## 5. Implementation Order

```
1. Verify merge quality of metagateway.py ← DONE (clean)
2. Write SMART component tests (semantic_cache, smart_router, context_budget)
3. Apply edge case fixes (thread safety, empty query, budget clamp)
4. Verify n8n integration files for correctness
5. Run tests to confirm no regressions
6. Update MASTER_OPTIMIZATION_PLAN.md with Phase 1b status
```

## 6. Open Questions

1. Should `semantic_cache.py` use persistent storage path from env var or default location in `.aiwg/`?
2. Should `smart_router.py` log every routing decision to KuzuDB for traceability?
3. The embedding fallback in `smart_router.py` imports from `dummie_sdk.routing.strategies` — the n8n agent modified this package. Need to verify the embedding strategy API hasn't changed.