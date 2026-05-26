---
spec_id: 194_memory_context_pruning
title: Memory Context Pruning with RIR Scoring + Token Budget
status: ACTIVE
layer: L2
last_verified_on: '2026-05-21'
version: 1.0.0
claims:
- id: 194_memory_context_pruning-file-valid
  description: Spec file '194_memory_context_pruning.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/194_memory_context_pruning.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 194: Memory Context Pruning

## Purpose
Define and implement a metacognitive hook that scores memory context items using RIR (Relevance-Importance-Recency), enforces a token budget per cognitive cycle, and compresses/prunes low-value context before it reaches the LLM.

## Canonical Implementation
- Hook module: `layers/l2_brain/metacognition/context_pruning.py`
- Scoring: `ContextPruningHook` uses `generate_vector()` for embedding similarity + RIR hybrid score
- Token budgeting: `max_context_tokens` configurable via env `DUMMIE_MAX_CONTEXT_TOKENS` (default 4096)
- Pipeline position: after `ContextEnricherHook`, before `SemanticToolSelectorHook`

## Physical Evidence
- `layers/l2_brain/metacognition/context_pruning.py`
- daemon.py wiring line: `ContextPruningHook(kuzu_repository=self.kuzu)` in `input_hooks`

## RIR Scoring Formula

```
RIR(v, q) = alpha * R(v, q) + beta * I(v) + gamma * F(v)

Where:
  R(v, q) = cosine_similarity(embedding(v), embedding(q))
  I(v)    = normalized importance score from authority_a + intent_i + proof_evidence
  F(v)    = normalized freshness score from lamport_t decay (exp(-delta/100))
  alpha   = 0.5 (Relevance weight)
  beta    = 0.3 (Importance weight)
  gamma   = 0.2 (Freshness/Recency weight)
```

### Authority → Importance Mapping
- HUMAN = 1.0, OVERSEER = 0.9, ARCHITECT = 0.8, ENGINEER = 0.7, AGENT = 0.5, unknown = 0.3

### Intent Type → Importance Bonus
- CRYSTALLIZATION = +0.15, RESOLUTION = +0.10, AUDIT = +0.05, MUTATION = +0.0, FABRICATION = -0.05, OBSERVATION = -0.10

## Token Budget Enforcement
- Items with RIR < 0.15 are dropped entirely
- Items with RIR between 0.15–0.35 are compressed (summary only, 120 chars)
- Items with RIR > 0.35 are preserved (full text, capped at 1024 chars each)
- Cumulative token count enforced: when total > `max_context_tokens`, lowest-score items are demoted (preserve→compress→drop)

## Integration Points
- **LLMLingua-2 Ready**: When `llmlongua-2` or similar compressor is available, replace the truncation-based `_compress_text` with a model-based compressor
- **RetrievalService compatible**: RIR scores can be used alongside or replace `RetrievalService.calculate_epistemic_score()` in future versions

## Edge Cases
- Empty memory context → no-op, telemetry records `pruned_items=0`
- Kuzu unavailable → graceful degrade, hook runs with whatever context is in `frame.telemetry`
- All items below RIR threshold → telemetry records `empty_after_pruning=true`
- Token budget too small for highest-RIR item → override, keep at least 1 item

## Verification Commands
```bash
```

## Backward Compatibility
- Existing `ContextEnricherHook` remains as placeholder for future Kuzu-backed memory enrichment
- This hook does not replace the existing `LocalContextCompressor` — both serve different pipeline phases
- `MetacognitiveFrame` contract unchanged; pruned context stored in `telemetry["pruned_context"]`
