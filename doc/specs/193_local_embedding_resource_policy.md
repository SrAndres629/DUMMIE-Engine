---
spec_id: 193_local_embedding_resource_policy
title: Local Embedding Resource Policy
status: ACTIVE
layer: L2
last_verified_on: '2026-05-20'
version: 1.0.0
claims:
- id: 193_local_embedding_resource_policy-file-valid
  description: Spec file '193_local_embedding_resource_policy.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/193_local_embedding_resource_policy.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 193: Local Embedding Resource Policy

## Purpose
Define mandatory production rules for local embeddings so DUMMIE can use cached local models without saturating CPU, RAM, GPU, or VRAM.

## Canonical Implementation
- Embedding SSoT: `layers/l2_brain/embedding_mesh/specialized_providers.py`
- Runtime router: `layers/l2_brain/embedding_mesh/router.py`
- Production verification: `layers/l2_brain/metacognition/production_verification.py`

## Physical Evidence
- `layers/l2_brain/embedding_mesh/specialized_providers.py`
- `layers/l2_brain/embedding_mesh/router.py`
- `layers/l2_brain/metacognition/production_verification.py`

## Hardware Policy
- `TEXT_FAST` uses `NomicEmbedProvider` via fastembed, CPU-first, 768 dimensions.
- `CODE` uses `CodeEmbeddingProvider` via fastembed, CPU-first, 384 dimensions.
- `TEXT_FIDELITY` uses `BGEM3Provider`, CPU by default, 1024 dimensions.
- GPU for BGE-M3 is opt-in only through `DUMMIE_BGE_M3_DEVICE=cuda`.
- General sentence-transformer embeddings are CPU by default through `DUMMIE_GENERAL_EMBED_DEVICE=cpu`.
- Do not load BGE-M3 on CUDA while daemon, Ollama, browser automation, or another embedding process is active unless VRAM headroom has been verified.

## Local llama.cpp Policy
- `llama-cpp-python` is installed via `uv` for future GGUF-backed local inference and embedding experiments.
- llama.cpp MUST NOT replace the canonical `EmbeddingRouter` until a GGUF embedding model is configured, benchmarked, and verified in production.
- Any llama.cpp embedding provider must expose the same `EmbeddingResponse` contract and must report degraded=false only after a real vector operation.

## Verification Commands
- `HF_HUB_OFFLINE=1 uv run python -c "from layers.l2_brain.embedding_mesh.specialized_providers import BGEM3Provider; from layers.l2_brain.embedding_mesh.contracts import EmbeddingRequest, EmbeddingCapability; r=BGEM3Provider().embed(EmbeddingRequest(content='verify', capability=EmbeddingCapability.TEXT_FIDELITY)); print(r.dimensions, r.degraded)"`
- `uv run python -m pytest layers/l2_brain/tests/test_embedding_mesh_router.py layers/l2_brain/tests/test_embedding_mesh_contracts.py layers/l2_brain/tests/test_vault_embedding_index.py -q --no-header --tb=short`

## Non-Negotiables
- No silent fallback may be reported as operational.
- Production verification fails if any required provider (`TEXT_FAST`, `TEXT_FIDELITY`, `CODE`) is degraded.
- Prefer CPU stability over GPU speed for embeddings unless a resource governor proves safe GPU use.
