---
spec_id: 122_embedding_adapter
title: 122 Embedding Adapter
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_1
last_verified_on: '2026-05-16'
claims:
- id: 122_embedding_adapter-file-valid
  description: Spec file '122_embedding_adapter.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/122_embedding_adapter.md').read().split('---')[1]); assert d,
    'empty frontmatter'"
  severity: critical
---
# Spec 122: Embedding Adapter

## Purpose
Provide a unified interface for text embeddings with a mandatory offline deterministic fallback to ensure semantic retrieval capability is always available without external dependencies.

## Scope
- `EmbeddingAdapter` base class.
- `DeterministicHashEmbeddingAdapter` (offline fallback).
- `DisabledProviderEmbeddingAdapter` (placeholder for real providers).
- `EmbeddingAdapterRegistry`.

## Runtime Behavior
1. `embed_text` accepts a string and returns an `EmbeddingResult`.
2. `DeterministicHashEmbeddingAdapter` uses SHA-256 to project text into a stable N-dimensional vector.
3. Vectors are normalized by default.
4. Cosine similarity implementation is provided by the base class.
5. Real providers are enabled by default (FastEmbed BAAI/bge-small-en-v1.5, 384-dim). Configuration optional for overrides.

## Inputs
- Text string.
- Optional adapter selection.

## Outputs
- `EmbeddingResult` containing vector, metadata, and status.

## Safety Rules
- No API keys required for fallback.
- No external network calls by default.
- Reject inputs that look like secrets or private chain-of-thought (heuristically).
- Vectors must be JSON serializable.

## Current State
- TBD

## Physical Evidence
- TBD

## Contract Invariants
- TBD

## Verification
- TBD

## Traceability
- TBD
