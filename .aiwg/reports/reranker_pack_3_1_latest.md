# Technical Report — Pack 3.1: Reranker Real or Hybrid+

This report outlines the structural details, dynamic degradation model, and verification results of the **Hybrid+** reranker implementation.

---

## 1. Dimensional Architecture

To avoid architectural overclaiming, the reranker distinguishes semantic input capabilities from the machine learning inference model.

### 1.1 Dynamic Degradation Formula
```python
degraded = semantic_input_degraded or reranker_engine_degraded
```
- **`semantic_input_degraded`**: `False` if and only if both the query and candidate items utilize the compatible `text_fast_bge_small_384` vector space with valid embeddings.
- **`reranker_engine_degraded`**: `True` because the system runs deterministic heuristic math offline, as no ML cross-encoder model is active in this phase.

### 1.2 Multi-Mode Selector
The reranker publishes the following `ranking_mode` statuses:
- `hybrid_real_embeddings`: Using real kompatible local embeddings with heuristic scoring.
- `hybrid_deterministic_fallback`: Operating under placeholder/hash fallback.
- `bypass_vector_similarity`: Pure vector similarity sorting under rollback instructions.

---

## 2. Score Weighting Scheme
The score is calculated as a weighted combination of six distinct dimensions:

| Component Name | Weight | Purpose |
| :--- | :--- | :--- |
| **`vector_similarity`** | `0.35` | Cosine similarity between vectors |
| **`token_overlap`** | `0.30` | Keyword matching density |
| **`path_overlap`** | `0.15` | Structural path relevance matching |
| **`contextual_boost`** | `0.10` | Semantic target matching adjustments |
| **`recency_freshness`** | `0.05` | Dynamic age-based score modulation |
| **`importance_truth_rank`** | `0.05` | Centralized repository importance ranking |

*Note: All scores are normalized strictly in the `[0.0, 1.0]` range before applying weights. Penalties (e.g. for legacy or shadow files) are subtracted from this final sum.*

---

## 3. Rollback & Bypass Strategy
If anomalous results or latency issues are encountered, the system provides a safe bypass:
- Triggered by passing the `bypass=True` parameter or setting the environment variable `DUMMIE_RERANK_BYPASS=1`.
- Ranks candidates solely by their raw `vector_similarity`.
- Marks `degraded = True` and sets mode to `bypass_vector_similarity`.

---

## 4. Verification Evidence

A regression suite of 10 automated tests has been executed and verified:
- **`test_weights_sum_to_one`** — PASS
- **`test_real_text_fast_vectors_set_semantic_input_not_degraded`** — PASS
- **`test_fallback_vectors_keep_response_degraded`** — PASS
- **`test_vector_space_mismatch_is_degraded_and_does_not_crash`** — PASS
- **`test_freshness_changes_ranking`** — PASS
- **`test_truth_rank_changes_ranking`** — PASS
- **`test_corrupt_metadata_does_not_crash`** — PASS
- **`test_path_overlap_affects_score`** — PASS
- **`test_bypass_mode_orders_by_vector_similarity`** — PASS
- **`test_diagnostics_explain_component_scores`** — PASS

---

## 5. Next Phase Recommendation
**Pack 3.2 — CODE Embedding Provider**: Isolating the lexical space of the AST parser from the general text corpus.
