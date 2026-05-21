---
spec_id: "192_embedding_mesh_foundation"
title: "EmbeddingMesh Foundation and Repo Self-Knowledge"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-20"
---

# Specification 192 — EmbeddingMesh Foundation & Repo Self-Knowledge

## Purpose
Establish a sovereign, typed, multi-capability, and offline-resilient embedding mesh that provides repository self-perception. DUMMIE Engine uses this package to map, classify, and audit active modules, tests, specifications, and configs.

## Current State
Fully implemented with REAL embeddings (not SHA256 fallback). Multiple specialized providers operational.

## Physical Evidence
- Core Module: `layers/l2_brain/embedding_mesh/__init__.py`
- Registry Module: `layers/l2_brain/embedding_mesh/registry.py`
- Router Module: `layers/l2_brain/embedding_mesh/router.py`
- Providers Module: `layers/l2_brain/embedding_mesh/providers.py`
- Specialized Providers: `layers/l2_brain/embedding_mesh/specialized_providers.py`
- Reranker Module: `layers/l2_brain/embedding_mesh/reranker.py`
- Indexer Module: `layers/l2_brain/embedding_mesh/repo_indexer.py`
- Matrix Module: `layers/l2_brain/embedding_mesh/hardening_matrix.py`
- Canonical Interface: `generate_vector()`, `generate_embedding()`, and `get_embedding_status()` in `specialized_providers.py`
- Indexer Script: `scripts/build_semantic_hardening_index.py`
- Test suite: `layers/l2_brain/tests/test_embedding_mesh_contracts.py`
- Test suite: `layers/l2_brain/tests/test_embedding_mesh_router.py`
- Test suite: `layers/l2_brain/tests/test_semantic_hardening_index.py`
- Index JSON: `.aiwg/reports/semantic_repo_index_latest.json`
- Index Markdown: `.aiwg/reports/semantic_repo_index_latest.md`
- Matrix JSON: `.aiwg/reports/semantic_hardening_matrix_latest.json`
- Matrix Markdown: `.aiwg/reports/semantic_hardening_matrix_latest.md`

## Contract Invariants
- **Vector Space Separation**: Vectors from different models/capabilities belong to distinct, non-comparable Vector Spaces. Comparing vectors from incompatible spaces must be prevented or flag warnings.
- **Deterministic Fallbacks**: Full offline compatibility is mandatory. If `fastembed` is unavailable, the registry automatically resolves requests using a deterministic hash projection (`degraded=True`).
- **Hexagonal Architecture**: The mesh operates within L2 Brain under clear boundaries, exposing contracts separate from legacy structures to avoid breaking existing layers.
- **Real Embeddings Mandatory**: Production usage MUST use real embedding providers (fastembed, sentence-transformers). SHA256 fallback is ONLY for degradation scenarios.

## Active Providers (Verified 2026-05-20)
| Provider | Model | Dimensions | Purpose | Status |
|----------|-------|------------|---------|--------|
| FastEmbedTextProvider | BAAI/bge-small-en-v1.5 | 384 | Fast text embeddings | ✅ Operational |
| CodeEmbeddingProvider | BAAI/bge-small-en-v1.5 + code preprocess | 384 | Code embeddings | ✅ Operational |
| NomicEmbedProvider | nomic-embed-text-v1.5 | 768 | Long context (8192) | ✅ Operational |
| BGEM3Provider | BAAI/bge-m3 | 1024 | Multilingual, dense+sparse | ✅ Operational |
| DeterministicFallbackProvider | SHA256 projection | 384 | Offline fallback | ✅ Available |

## Canonical Interface
```python
from layers.l2_brain.embedding_mesh.specialized_providers import generate_vector, generate_embedding, get_embedding_status

# Auto-routes to optimal provider based on content type
vec = generate_vector("def foo(x): return x + 1")  # → CodeEmbeddingProvider (384d)
vec = generate_vector("The architecture uses hexagonal patterns")  # → NomicEmbedProvider (768d)

# Use metadata-aware API for retrieval/ranking
resp = generate_embedding("The architecture uses hexagonal patterns")
assert resp.vector_space == "text_fast_nomic_768"

# Check provider status
status = get_embedding_status()
# Returns: {"TEXT_FAST": {...}, "TEXT_FIDELITY": {...}, "CODE": {...}, "FALLBACK": {...}}
```

## Verification
Run tests via pytest:
```bash
uv run python -m pytest layers/l2_brain/tests/test_embedding_mesh_contracts.py layers/l2_brain/tests/test_embedding_mesh_router.py layers/l2_brain/tests/test_semantic_hardening_index.py
```

Run CLI indexer:
```bash
uv run python scripts/build_semantic_hardening_index.py --repo-root . --write-reports
```

Verify real embeddings:
```bash
uv run python -c "
from layers.l2_brain.embedding_mesh.specialized_providers import generate_vector, get_embedding_status
vec = generate_vector('test')
print(f'Vector dim: {len(vec)} (should be 384, 768, or 1024, NOT 8)')
status = get_embedding_status()
print(f'Active providers: {len([k for k, v in status.items() if not v.get(\"degraded\", True)])}')
"
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md`
- Related files:
  - `doc/specs/192_embedding_mesh_foundation.feature`
  - `doc/specs/192_embedding_mesh_foundation.rules.json`
- Consumers:
  - `layers/l2_brain/memory/models.py` (MemoryNode4D embeddings)
  - `layers/l2_brain/infrastructure/kuzu.py` (semantic search)
  - `layers/l2_brain/cognition/context_nutrition.py` (context nutrition)
  - `layers/l2_brain/memory/vault_embedding_index.py` (vault indexing)
  - `layers/l2_brain/metacognition/tool_selector.py` (tool scoring)
  - `layers/l2_brain/metacognition/production_verification.py` (verification hook)
