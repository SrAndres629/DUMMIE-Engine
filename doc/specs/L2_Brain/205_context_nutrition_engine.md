---
spec_id: "205_context_nutrition_engine"
title: "Context Nutrition Engine (CNE)"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-20"
version: "1.1.0"
---

## Purpose
The Context Nutrition Engine (CNE) transforms raw user prompts into evidence-grounded context packets. It reduces hallucinations, exposes semantic gaps, preserves 4D-TES causal evidence, and keeps prompt context under a token budget.

## Architecture
The CNE sits above canonical 4D-TES retrieval:

```text
user prompt
→ ContextNutritionEngine.nutrate()
→ KuzuRepository.hybrid_search()
→ CanonicalEmbeddingAdapter.generate_vector()
→ MMR/token-budget selection
→ evidence-grounded nutrated prompt
```

Current implementation:
- `layers/l2_brain/cognition/context_nutrition.py`
- `layers/l2_brain/src/brain/infrastructure/adapters/kuzu_repository.py`
- `layers/l2_brain/src/brain/infrastructure/adapters/embedding_adapter.py`
- `dummie/runtime_chat.py` (Wiring)

## Contract Invariants
- **SSoT:** Memory retrieval MUST go through canonical Kùzu/4D-TES. 
- **No false semantics:** Retrieval MUST NOT compute cosine similarity across incompatible vector spaces.
- **MMR Diversity:** Use Maximal Marginal Relevance to select a diverse set of evidence nodes.
- **Ignorant Mode:** If coherence score < 0.4, activate IGNORANT_MODE to prevent hallucinations.
- **Token Budget:** Automatically fit nutrated prompt within the specified token budget.

## Verification
```bash
export PYTHONPATH=$PYTHONPATH:.
uv run python -c "from dummie.runtime_chat import DummieRuntimeChat; chat = DummieRuntimeChat(); res = chat.run('Test canonical wiring'); print(res.raw_data['preprocessing']['cne_report'])"
```
