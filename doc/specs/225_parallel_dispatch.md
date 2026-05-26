---
status: SUPERSEDED
claims:
- id: conjunction_splitters
  description: Splitters de conjuncion implementados
  severity: critical
- id: parallel_mode
  description: mode=parallel soportado en dummie_process
  severity: critical
implementations:
- file: layers/l1_nervous/tools.py
  function: dummie_process
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Parallel Sub-Intent Dispatch

**Date:** 2026-05-26  
**Phase:** 2d  
**Requires reboot:** No  
**Depends on:** Spec 228 (collaborative gateway)  
**Files modified:** `tools.py`

## 1. Purpose

LLM agents often express compound intents: "find test file AND run tests", "search for errors AND create a fix branch". Currently the gateway processes these sequentially — one intent at a time. This spec adds conjunction detection and parallel sub-intent dispatch, reducing latency for compound queries.

## 2. Design

### 2.1 Conjunction detection

A lightweight regex-based splitter (no LLM required):

```python
SPLITTERS = [
    r"\band\b(?:\s+then\b)?",     # "find file and then run tests" → 2 intents
    r"\bademás\b",                 # Spanish: "buscar archivo y además ejecutar"
    r"\btambién\b",                # Spanish: "buscar archivo y también tests"
    r";\s*",                       # semicolons
    r"\.\s+(?!\d)",                # period followed by space and non-digit
]
```

### 2.2 Mode

New mode parameter `"parallel"` or auto-detection in `"auto"` mode when conjunctions found.

When mode is `"auto"` and conjunctions are detected:
1. Split intent into sub-intents
2. Return plan with `parallel_groups` showing which can run simultaneously
3. Agent can confirm (execute all in parallel) or reject

When mode is `"parallel"`:
1. Split intent
2. Execute all sub-intents via `asyncio.gather`
3. Return consolidated results

### 2.3 Response format

```json
{
  "mode": "parallel",
  "intent": "find test file AND run tests",
  "sub_intents": [
    {"intent": "find test file", "result": {...}},
    {"intent": "run tests", "result": {...}}
  ],
  "parallel_groups": [[0], [1]],
  "total_latency_ms": 150,
  "sequential_latency_ms": 280
}
```

## 3. Implementation

### 3.1 Core logic in tools.py

```python
CONJUNCTION_SPLITTERS = [
    re.compile(r"\band\b(?:\s+then\b)?", re.IGNORECASE),
    re.compile(r"\bademás\b", re.IGNORECASE),
    re.compile(r"\btambién\b", re.IGNORECASE),
    re.compile(r";\s*"),
    re.compile(r"\.\s+(?!\d)"),
]

def _split_compound(intent: str) -> list[str]:
    """Split compound intent into independent sub-intents."""
    merged = intent
    for pattern in CONJUNCTION_SPLITTERS:
        parts = pattern.split(merged)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
    return [intent]
```

### 3.2 Integration into dummie_process

Add `mode="parallel"` handling. In `mode="auto"`, detect conjunctions and treat as plan (show sub-intents before executing).

## 4. Agent experience

```
Agent: dummie_process("find test_user.py AND run pytest", mode="parallel")
Gateway: 
  → Executes both intents in parallel via asyncio.gather
  → Returns consolidated result with per-sub-intent latency

Agent: dummie_process("search for error AND create fix branch", mode="auto")
Gateway:
  → Detects conjunction
  → Returns plan with 2 sub-intents + parallel_groups
  → Agent calls confirm to execute
```

## 5. Success criteria

- `_split_compound("a AND b")` → `["a", "b"]`
- `_split_compound("a y además b")` → `["a y", "b"]`
- `_split_compound("simple query")` → `["simple query"]`
- `mode="parallel"` executes sub-intents concurrently
- Consolidated response includes per-sub-intent results and latency savings