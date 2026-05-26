---
spec_id: DE-PHASE9-VEI-90
title: Vault Embedding Index
status: ACTIVE
layer: L2
last_verified_on: '2026-05-20'
priority: MANDATORY
version: 2.0.0
namespace: dummie.engine.l2
claims:
- id: 90_vault_embedding_index-file-valid
  description: Spec file '90_vault_embedding_index.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/90_vault_embedding_index.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Vault Embedding Index

## Purpose
Provide a layer for semantic retrieval and knowledge indexing using REAL embeddings via EmbeddingRouter.

## Current State
Implemented in `layers/l2_brain/memory/vault_embedding_index.py`. Uses real embeddings from `EmbeddingRouter` (Spec 192) with deterministic SHA256 fallback only when providers unavailable.

## Physical Evidence
- `layers/l2_brain/memory/vault_embedding_index.py`
- `.aiwg/schemas/vault_embedding_index.schema.json`
- `.aiwg/vault/vault_embedding_index.json` (runtime index)

## Contract Invariants
- **Real Embeddings First**: MUST use `EmbeddingRouter.generate_vector()` for all indexing and search operations.
- **Deterministic Fallback**: Only when EmbeddingRouter unavailable, falls back to SHA256 projection (384 dimensions).
- **Model Tracking**: Each indexed entry records `embedding_model` to flag cross-model comparisons.
- **Cross-Model Penalty**: Similarity scores reduced by 20% when comparing vectors from different models.
- **Idempotent**: Indexing the same content (same vault_id + content_hash) results in no change.
- **Searchable**: Cosine similarity search with top_k retrieval.

## Migration from v1 to v2
- v1: Used 8-dimensional SHA256 hash vectors (`deterministic-hash-v1`)
- v2: Uses real embeddings (384-1024 dimensions) via EmbeddingRouter
- Migration: Existing entries will be re-indexed on next `index_entry()` call
- To force full rebuild: call `rebuild_index()` with all vault entries

## Verification
```bash
uv run python -c "
from layers.l2_brain.memory.vault_embedding_index import VaultEmbeddingIndex
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    index = VaultEmbeddingIndex(root=tmpdir)
    
    # Index test entries
    index.index_entry({
        'vault_id': 'test-1',
        'content_hash': 'sha256:abc',
        'summary': 'Decision to use KuzuDB for graph persistence'
    })
    
    # Search and verify real embeddings
    results = index.search_similar('graph database')
    assert len(results) > 0, 'Should find results'
    assert results[0]['vault_id'] == 'test-1', 'Most relevant should be KuzuDB decision'
    
    # Verify model is not fake hash
    entries = index.get_all_entries()
    model = entries['test-1']['embedding_model']
    assert model != 'deterministic-hash-v1', f'Should use real embeddings, got {model}'
    assert len(entries['test-1']['vector']) >= 384, f'Vector should be >= 384d, got {len(entries[\"test-1\"][\"vector\"])}d'
    
    print(f'✅ Vault Embedding Index verified: model={model}, dim={len(entries[\"test-1\"][\"vector\"])}')
"
```

## Traceability
- **Missions**: `demo_refactor_snowball`
- **Layers**: `L2_BRAIN`
- **Files**: `layers/l2_brain/memory/vault_embedding_index.py`
- **Dependencies**: Spec 192 (EmbeddingMesh Foundation)
