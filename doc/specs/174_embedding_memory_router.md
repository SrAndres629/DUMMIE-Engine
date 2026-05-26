---
spec_id: 174_embedding_memory_router
title: Embedding Memory Router
status: ACTIVE
layer: L2
last_verified_on: '2026-05-20'
version: 2.0.0
dependencies:
- specs/192_embedding_mesh_foundation.md
- specs/L2_Brain/90_vault_embedding_index.md
claims:
- id: 174_embedding_memory_router-file-valid
  description: Spec file '174_embedding_memory_router.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/174_embedding_memory_router.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
This spec establishes the embedding memory router (HEARTBEAT-2) to safely index high-value context items and provide a local search/retrieval mechanism using REAL embeddings via EmbeddingRouter.

## Current State
**v2.0.0:** Fully operational with real embeddings via `EmbeddingRouter.generate_vector()`. Deterministic fallback only when providers unavailable.

## Physical Evidence
- Core module: `layers/l2_brain/embedding_mesh/specialized_providers.py` (EmbeddingRouter)
- Canonical interface: `generate_vector(text, hint)`, `generate_embedding(text, hint)`, and `get_embedding_status()`
- Memory integration: `layers/l2_brain/memory/models.py` (MemoryNode4D.from_intent_context)
- Kuzu integration: `layers/l2_brain/infrastructure/kuzu.py` (KuzuMemory.semantic_search)
- Vault integration: `layers/l2_brain/memory/vault_embedding_index.py` (VaultEmbeddingIndex)
- Test suite: `layers/l2_brain/tests/test_embedding_memory_router.py`
- JSON Schema: `.aiwg/schemas/embedding_memory_router.schema.json`
- Output reports: `.aiwg/reports/embedding_memory_router_latest.json` and `.aiwg/reports/embedding_memory_router_latest.md`

## Contract Invariants
- **Real Embeddings First**: MUST use `EmbeddingRouter.generate_vector()` for all indexing and search operations. Supports 4 providers: TEXT_FAST (768d), TEXT_FIDELITY (1024d), CODE (384d), FALLBACK (384d).
- **Deterministic Offline Fallback**: Under local security limits, must fall back to a deterministic model (`DETERMINISTIC_FALLBACK` or `PROVIDER_DISABLED`) and issue appropriate warnings.
- **API Guard**: Must never make network calls or require API keys. HF_HUB_OFFLINE=1 when models are cached locally.
- **Surgical Indexing**: Indexes only the high-value 6D context items rather than loading the entire codebase.
- **Vector Space Separation**: Vectors from different models belong to distinct, non-comparable Vector Spaces. Cross-model comparisons must be blocked for cosine scoring or explicitly marked incompatible.
- **Model Tracking**: Retrieval paths must preserve vector-space metadata. Legacy Kùzu rows without `vector_space` may infer the space from vector dimensions but must not claim false compatibility.

## Active Providers (Verified 2026-05-20)
| Provider | Model | Dimensions | Purpose | Status |
|----------|-------|------------|---------|--------|
| NomicEmbedProvider | nomic-embed-text-v1.5 | 768 | Long context (8192) | ✅ Operational |
| BGEM3Provider | BAAI/bge-m3 | 1024 | Multilingual, dense+sparse | ✅ Operational |
| CodeEmbeddingProvider | BAAI/bge-small-en-v1.5 + code preprocess | 384 | Code embeddings | ✅ Operational |
| DeterministicFallbackProvider | SHA256 projection | 384 | Offline fallback | ✅ Available |

## Canonical Interface
```python
from layers.l2_brain.embedding_mesh.specialized_providers import generate_vector, generate_embedding, get_embedding_status

# Auto-routes to optimal provider based on content type
vec = generate_vector("def foo(x): return x + 1")  # → CodeEmbeddingProvider (384d)
vec = generate_vector("The architecture uses hexagonal patterns")  # → NomicEmbedProvider (768d)

# Check provider status
status = get_embedding_status()
# Returns: {"TEXT_FAST": {...}, "TEXT_FIDELITY": {...}, "CODE": {...}, "FALLBACK": {...}}

resp = generate_embedding("semantic retrieval")
# Returns vector + vector_space + degraded/model metadata for safe ranking
```

## Verification
Run tests via pytest:
```bash
uv run python -m pytest layers/l2_brain/tests/test_embedding_memory_router.py
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
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `embedding_memory_router.schema.json`
- Related specs: `doc/specs/192_embedding_mesh_foundation.md`
- Related specs: `doc/specs/L2_Brain/90_vault_embedding_index.md`
- Consumers: `layers/l2_brain/memory/models.py`, `layers/l2_brain/infrastructure/kuzu.py`, `layers/l2_brain/memory/vault_embedding_index.py`, `layers/l2_brain/metacognition/tool_selector.py`
