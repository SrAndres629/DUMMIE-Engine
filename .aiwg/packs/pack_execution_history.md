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

---

## 8. PACK_5.1: Eliminar 27 huérfanos flat_brain
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: 10/27 true orphans deleted, 17 restored from LEGACY backup
* **Lessons**: Most "orphans" had indirect references; verify with `rg -n` before deletion.

---

## 9. PACK_5.2: Migrar flat_brain con spec
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: 68 files + 8 subdirectories removed (had canonical equivalents)
* **Lessons**: Shim session_store.py required for backward compat during transition.

---

## 10. PACK_5.3: Eliminar re-export shims
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: daemon, daemon_diagnostic, model_router, metacognition/contracts shims removed
* **Lessons**: Shims masked import bugs for 2+ months (redirector hid indent errors).

---

## 11. PACK_5.4: Remover _FlatBrainFallbackFinder
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: FallbackFinder removed from sys.meta_path. 19 modules migrated.
* **Lessons**: Never use opaque redirectors that silently resolve imports.

---

## 12. PACK_5.5: Eliminar flat_brain/ completo
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: flat_brain/ reduced from ~230 → 0 files.
* **Lessons**: Cleanup requires migration order: modules first, then delete.

---

## 13. PACK_5.6: Test contrato flat_brain no existe
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: Test verifies no canonical module imports from flat_brain.
* **Lessons**: Contract tests prevent regression into legacy layout.

---

## 14. PACK_5.7: ContextPruningHook
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: RIR metadata + scoring integrated into metacognitive pipeline.
* **Lessons**: Pruning thresholds (0.20/0.45) prevent context overflow on laptop.

---

## 15. PACK_6: src/brain/ canonical migration
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: src/brain/ deleted (47 files). 23 tests passing.
* **Lessons**: 133 `brain.` → `layers.l2_brain.` imports fixed across 49 files.

---

## 16. PACK_7: Spec registry completeness
* **Status**: `COMPLETED`
* **Commit**: `fe91a2f`
* **Metrics After**: 180 specs discovered, 169 evidence paths corrected, 26 canonical path fixes. Error count 41→21.
* **Lessons**: glob→rglob required for recursive .md discovery. False positives from function-name-as-path remain.

---

## 17. PACK_8: End-to-end production verification
* **Status**: `COMPLETED`
* **Commit**: `80a6445`
* **Metrics After**: Ollama RUNNING (gemma3:1b), embeddings 768d real, KuzuRepository initialized, SkillRegistry 32+6+19 skills, Import chain PASS.
* **Lessons**: Full chain verified: embed → store → retrieve → route → respond.

---

## 18. PACK_9: Performance optimization for laptop deployment
* **Status**: `COMPLETED`
* **Commit**: `d4e2247`
* **Metrics After**: Lazy loading for heavy components, aggressive context pruning (RIR 0.20/0.45), dynamic token budgeting (1024/2048/4096), embedding LRU cache (500 entries, 30min TTL), optimized swarm daemon (30s polling).
* **Lessons**: Target 50% memory reduction (3.1GB→1.5GB). Tests: 41/41 PASS.

---

## 19. PACK_LEGACY: Eliminar flat_brain_LEGACY
* **Status**: `COMPLETED`
* **Commit**: `fe91a2f`
* **Metrics After**: 238 files, 5.8MB backup removed. 0 code references.
* **Lessons**: LEGACY backup no longer needed once flat_brain/ confirmación is complete.

---

## 21. PACK_3.2: CODE Embedding Provider
* **Status**: `COMPLETED`
* **Commit**: `pending`
* **Metrics After**: FastEmbedCodeProvider uses shared model cache with TEXT_FAST (zero additional memory). CODE vectors stored under `CODE_LOCAL_768` space, isolated from `TEXT_FAST_BGE_SMALL_384`. ASTBlastRadiusIndexer generates CODE embeddings for parsed symbols.
* **Tests**: 6 new tests PASS. Embedding mesh: 11/11 PASS. Import chain: PASS.
* **Lessons**: Same model, separate vector space achieves semantic isolation without extra compute. Module-level `_MODEL_CACHE` prevents double model loading.

## 22. INMEDIATO: Branch cleanup + merge
* **Status**: `COMPLETED`
* **Commit**: `fe91a2f`
* **Metrics After**: Fast-forward merge to main, 6 stale branches removed, backup branches preserved.
* **Lessons**: Always verify `git diff` after batch sed replacements to avoid double-prefix corruption.
