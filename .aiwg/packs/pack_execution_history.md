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

---

## 3. AIWG_KERNEL_0.1: AIWG Kernel Governance Infrastructure
* **Status**: `COMPLETED`
* **Commit**: `564a6cfef70a597a87e596a707a0cd0a5e913a44`
* **Lessons**: Initial schema and structure setup for pack guard CLI.

---

## 4. AIWG_KERNEL_0.2: AIWG Kernel Execution Evidence Runner
* **Status**: `COMPLETED`
* **Commit**: `679d57d10702714019745f2775152cba70f142f8`
* **Lessons**: Execution runner enables autonomous evidence capturing of pytest and spec checks.

---

## 5. AIWG_KERNEL_0.3: AIWG Kernel Integration & Resilience Guard
* **Status**: `COMPLETED`
* **Commit**: `e7de2dd5cd402e369d885ad84c67bc7a226d510d`
* **Lessons**: Integration of freshness and anti-overclaim gates.

---

## 6. AIWG_KERNEL_0.4: AIWG Kernel Freeze Consolidator
* **Status**: `COMPLETED`
* **Commit**: `bdb76320818c9fbd9f13f47ab5e18668aa08aff9`
* **Lessons**: Consolidated final freeze consistency for stable L2 brain development.

---

## 7. HEARTBEAT-3.2: AIWG Native Operating Kernel & Context Capsule Engine
* **Status**: `COMPLETED`
* **Metrics After**: Native `.aiwg` kernel is fully mandatory for agent execution (`guarded-run`). Incremental token indexer prevents raw folder reading. Token Economy checks now natively block overclaim. 
* **Repairs**: Implemented `aiwg_preflight`, `mutation_router`, `ContextCapsuleEngine`, `incremental_indexer`, and `ContextCapsuleCache`.
* **Lessons**: Agentic workflow is now strictly bounded by token budgets and explicitly routed through receipt-based execution records.
