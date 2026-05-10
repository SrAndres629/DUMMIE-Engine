import pytest
try:
    from layers.l2_brain.embedding_provider import EmbeddingProvider
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from embedding_provider import EmbeddingProvider

def test_embedding_generation():
    """Prueba que se genere un vector con la dimensión correcta (384)."""
    text = "DUMMIE Engine Semantic Memory"
    vector = EmbeddingProvider.generate_vector(text)
    
    assert isinstance(vector, list)
    assert len(vector) == 384
    assert any(v != 0 for v in vector)

def test_semantic_similarity():
    """Prueba que textos similares tengan mayor puntuación que distintos."""
    v1 = EmbeddingProvider.generate_vector("git commit changes")
    v2 = EmbeddingProvider.generate_vector("version control system")
    v3 = EmbeddingProvider.generate_vector("baking a cake")
    
    sim_similar = EmbeddingProvider.similarity(v1, v2)
    sim_different = EmbeddingProvider.similarity(v1, v3)
    
    print(f"Similarity (similar): {sim_similar}")
    print(f"Similarity (different): {sim_different}")
    
    assert sim_similar > sim_different
    assert sim_similar > 0.5
