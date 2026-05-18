import math
from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    EmbeddingCapability,
    EmbeddingRequest,
    VectorSpace,
    vector_spaces_compatible,
)
from layers.l2_brain.embedding_mesh.providers import DeterministicFallbackProvider

def test_deterministic_fallback_stability():
    provider = DeterministicFallbackProvider(dimensions=384)
    req1 = EmbeddingRequest(
        content="Stable DUMMIE Engine payload",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.FALLBACK
    )
    req2 = EmbeddingRequest(
        content="Stable DUMMIE Engine payload",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.FALLBACK
    )
    
    resp1 = provider.embed(req1)
    resp2 = provider.embed(req2)
    
    assert resp1.vector == resp2.vector
    assert resp1.dimensions == 384
    assert resp1.vector_space == VectorSpace.FALLBACK_HASH_384
    assert resp1.degraded is True
    assert resp1.model_used == "deterministic-sha256-projection"

def test_vector_normalization():
    provider = DeterministicFallbackProvider(dimensions=128)
    req = EmbeddingRequest(
        content="DUMMIE Engine structural hardening",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.FALLBACK
    )
    resp = provider.embed(req)
    assert len(resp.vector) == 128
    
    # Calculate magnitude
    mag = math.sqrt(sum(v*v for v in resp.vector))
    assert math.isclose(mag, 1.0, rel_tol=1e-5)
    assert resp.vector_space == "fallback_hash_128"


def test_vector_space_compatibility_is_strict():
    assert vector_spaces_compatible("code_local_768", "code_local_768")
    assert not vector_spaces_compatible("code_local_768", "text_fast_bge_small_384")
