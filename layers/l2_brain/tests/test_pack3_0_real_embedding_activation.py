# Regression test suite for Pack 3.0 - Real TEXT_FAST Embedding Provider
import math
from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    EmbeddingCapability,
    EmbeddingRequest,
    VectorSpace,
)
from layers.l2_brain.embedding_mesh.providers import (
    FastEmbedTextProvider,
    DeterministicFallbackProvider,
    PlaceholderCapabilityProvider,
)
from layers.l2_brain.embedding_mesh.registry import EmbeddingRegistry

def test_fast_embed_text_provider_real_activation():
    """Verifica que el proveedor FastEmbedTextProvider genera embeddings reales de 384 dims no degradados."""
    provider = FastEmbedTextProvider()
    req = EmbeddingRequest(
        content="DUMMIE Engine autonomous real embedding activation test",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.TEXT_FAST
    )
    
    response = provider.embed(req)
    
    assert response.degraded is False
    assert response.dimensions == 384
    assert len(response.vector) == 384
    assert response.vector_space == VectorSpace.TEXT_FAST_BGE_SMALL_384
    assert response.model_used == "BAAI/bge-small-en-v1.5"
    assert response.reason == ""

def test_fast_embed_text_provider_semantic_similarity():
    """Verifica que la similitud semántica calculada sobre los embeddings reales de fastembed es coherente."""
    provider = FastEmbedTextProvider()
    
    req1 = EmbeddingRequest(
        content="Machine learning neural network models",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.TEXT_FAST
    )
    req2 = EmbeddingRequest(
        content="Deep learning artificial intelligence networks",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.TEXT_FAST
    )
    req_unrelated = EmbeddingRequest(
        content="Cooking recipes for chocolate cake dessert",
        content_type=ContentType.TEXT,
        capability=EmbeddingCapability.TEXT_FAST
    )
    
    resp1 = provider.embed(req1)
    resp2 = provider.embed(req2)
    resp_unrelated = provider.embed(req_unrelated)
    
    # Calculate cosine similarity manually or via numpy
    import numpy as np
    def cosine_similarity(v1, v2):
        a, b = np.array(v1), np.array(v2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        
    sim_related = cosine_similarity(resp1.vector, resp2.vector)
    sim_unrelated = cosine_similarity(resp1.vector, resp_unrelated.vector)
    
    assert sim_related > sim_unrelated
    assert sim_related > 0.4  # semantic topics match

def test_registry_integration_and_placeholder_fallbacks():
    """Verifica que el registro de embeddings asigne correctamente los proveedores y use fallbacks para placeholders."""
    registry = EmbeddingRegistry()
    
    # 1. TEXT_FAST should map to FastEmbedTextProvider (real)
    fast_provider = registry.get_provider(EmbeddingCapability.TEXT_FAST)
    assert isinstance(fast_provider, FastEmbedTextProvider)
    
    # 2. CODE capability should map to PlaceholderCapabilityProvider which degrades
    code_provider = registry.get_provider(EmbeddingCapability.CODE)
    assert isinstance(code_provider, PlaceholderCapabilityProvider)
    
    req = EmbeddingRequest(
        content="func main() { fmt.Println(\"hello\") }",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE
    )
    resp = code_provider.embed(req)
    
    assert resp.degraded is True
    assert resp.dimensions == 384
    assert resp.vector_space == "fallback_hash_384"
    assert "placeholder" in resp.model_used
