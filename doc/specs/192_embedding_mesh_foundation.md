---
spec_id: "192_embedding_mesh_foundation"
title: "EmbeddingMesh Foundation and Repo Self-Knowledge"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-18"
---

# Specification 192 — EmbeddingMesh Foundation & Repo Self-Knowledge

## Purpose
Establish a sovereign, typed, multi-capability, and offline-resilient embedding mesh that provides repository self-perception. DUMMIE Engine uses this package to map, classify, and audit active modules, tests, specifications, and configs.

## Current State
Fully implemented and verified under green unit tests and indexer smoke checks.

## Physical Evidence
- Core Module: `layers/l2_brain/embedding_mesh/__init__.py`
- Registry Module: `layers/l2_brain/embedding_mesh/registry.py`
- Router Module: `layers/l2_brain/embedding_mesh/router.py`
- Providers Module: `layers/l2_brain/embedding_mesh/providers.py`
- Reranker Module: `layers/l2_brain/embedding_mesh/reranker.py`
- Indexer Module: `layers/l2_brain/embedding_mesh/repo_indexer.py`
- Matrix Module: `layers/l2_brain/embedding_mesh/hardening_matrix.py`
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

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_embedding_mesh_contracts.py layers/l2_brain/tests/test_embedding_mesh_router.py layers/l2_brain/tests/test_semantic_hardening_index.py
```

Run CLI indexer:
```bash
layers/l2_brain/.venv/bin/python scripts/build_semantic_hardening_index.py --repo-root . --write-reports
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md`
- Related files:
  - `doc/specs/192_embedding_mesh_foundation.feature`
  - `doc/specs/192_embedding_mesh_foundation.rules.json`
