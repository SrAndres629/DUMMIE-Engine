# Pack Execution History — DUMMIE Engine

This documents the history of closed development packs.

---

## 1. PACK_3.0: Real TEXT_FAST Embedding Provider
* **Status**: `COMPLETED`
* **Commit**: `e8e50be1e39a3f9e9cf2e259bde6b4129ec2e35f`
* **Metrics After**: `embedding_mode = REAL_LOCAL`, `degraded_embeddings = 717`
* **Lessons**: Local FastEmbed vectors perform with high similarity, and require python venv wrapper for report compilation.

---

## 2. PACK_3.1: Reranker Real or Hybrid+
* **Status**: `COMPLETED`
* **Commit**: `0c41fd25d6e38a244e716f653c8733d2fec1a657`
* **Metrics After**: `degraded_embeddings = 717`, `vector_spaces_used = ["fallback_hash_384", "none", "text_fast_bge_small_384"]`
* **Repairs**: Run indexer using `.venv` python directly, and added active semantic regression gate to test suite.
* **Lessons**: Strict regression gates prevent silent degradation of semantic provider space.
