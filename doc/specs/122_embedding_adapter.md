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
5. Real providers are disabled by default and require explicit configuration.

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
