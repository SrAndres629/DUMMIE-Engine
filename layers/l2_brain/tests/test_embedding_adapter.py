import pytest
from layers.l2_brain.embedding_mesh.embedding_adapter import (
    embed_text, 
    EmbeddingAdapterRegistry, 
    DeterministicHashEmbeddingAdapter,
    DisabledProviderEmbeddingAdapter
)

def test_deterministic_fallback_stability():
    text = "DUMMIE Engine"
    res1 = embed_text(text, adapter_name="fallback")
    res2 = embed_text(text, adapter_name="fallback")
    
    assert res1.status == "SUCCESS"
    assert res1.vector.vector == res2.vector.vector
    assert res1.vector.dim == 128
    # Check normalization
    norm = sum(v*v for v in res1.vector.vector)
    assert pytest.approx(norm, 0.001) == 1.0

def test_deterministic_fallback_difference():
    res1 = embed_text("Hello")
    res2 = embed_text("World")
    assert res1.vector.vector != res2.vector.vector

def test_cosine_similarity():
    adapter = DeterministicHashEmbeddingAdapter()
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    v3 = [1.0, 0.0, 0.0]
    
    assert adapter.similarity(v1, v1) == pytest.approx(1.0)
    assert adapter.similarity(v1, v2) == pytest.approx(0.0)
    assert adapter.similarity(v1, v3) == pytest.approx(1.0)

def test_provider_disabled_by_default():
    res = embed_text("test", adapter_name="provider")
    assert res.status == "PROVIDER_DISABLED"
    assert res.vector.dim == 0

def test_empty_text():
    res = embed_text("")
    assert res.status == "SUCCESS"
    assert all(v == 0.0 for v in res.vector.vector)
