---
spec_id: DE-PHASE8-MEMREF-88
title: Learning Episode Memory Integration
status: DRAFT
layer: L2
last_verified_on: '2025-05-15'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.l2
claims:
- id: 88_learning_episode_memory_integration-file-valid
  description: Spec file '88_learning_episode_memory_integration.md' exists, parses
    valid YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/88_learning_episode_memory_integration.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Learning Episode Memory Integration

## Purpose
Standardize the serialization and persistence of LearningEpisodes and bridge operational memory with persistent graph models via `MemoryRef`.

## Current State
Implemented in `layers/l2_brain/memory_refs.py`. Defines deterministic, path-safe references suitable for ingestion by Kuzu and vector embeddings.

## Physical Evidence
- `layers/l2_brain/learning_episode.py`
- `layers/l2_brain/session_store.py`
- `layers/l2_brain/memory_refs.py`
- `layers/l2_brain/tests/test_memory_refs.py`

## Contract Invariants
- **Deterministic Identity**: `MemoryRef` IDs are hashed from paths.
- **Path Safety**: Rejects absolute paths and path traversals (`..`).
- **Graph Readiness**: Contains `kuzu_ready` and `embedding_ready` boolean flags indicating processing state.

## Verification
```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_memory_refs.py
```

## Traceability
- **Missions**: `demo_refactor_snowball`
- **Layers**: `L2_BRAIN`
- **Files**: `layers/l2_brain/memory_refs.py`, `layers/l2_brain/learning_episode.py`
