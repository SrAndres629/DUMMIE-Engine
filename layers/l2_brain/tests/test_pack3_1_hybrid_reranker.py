# Regression test suite for Pack 3.1 - Hybrid Reranker Activation
from datetime import datetime, timezone, timedelta
from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    RerankRequest,
    VectorSpace,
)
from layers.l2_brain.embedding_mesh.reranker import HybridReranker

def test_hybrid_reranking_score_weights_and_boosts():
    """Verifica la correcta ponderación de pesos de texto, vector, boost y penalizaciones."""
    candidates = [
        {
            "text": "Core module optimization logic",
            "path": "layers/l2_brain/core.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {"embedding_degraded": False}
        },
        {
            "text": "Stale deprecated scratchpad legacy helper",
            "path": "doc/.deprecated/scratchpad/test.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {"embedding_degraded": False, "classification": "LEGACY"}
        }
    ]
    
    req = RerankRequest(
        query="Core module",
        candidates=candidates,
        top_k=2,
        content_type=ContentType.CODE
    )
    
    resp = HybridReranker.rerank(
        request=req,
        query_vector=[1.0, 0.0, 0.0],
        query_vector_space="text_fast_bge_small_384"
    )
    
    ranked = resp.ranked_candidates
    assert len(ranked) == 2
    
    # First candidate has high overlap and path matching + contextual boost, and no legacy penalty
    first = ranked[0]
    assert first["candidate"]["path"] == "layers/l2_brain/core.py"
    assert first["score"] > 0.5
    
    # Second candidate gets heavily penalized for LEGACY classification / path
    second = ranked[1]
    assert second["metrics"]["penalty"] > 0.0
    assert second["score"] < first["score"]

def test_hybrid_reranking_recency_and_importance():
    """Verifica que el reranker responda incrementalmente a la recencia (freshness) y a la importancia (truth_rank)."""
    now_utc = datetime.now(timezone.utc)
    fresh_ts = (now_utc - timedelta(days=2)).isoformat().replace("+00:00", "Z")
    stale_ts = (now_utc - timedelta(days=45)).isoformat().replace("+00:00", "Z")
    
    candidates = [
        {
            "text": "Feature implementation notes",
            "path": "doc/specs/feat.md",
            "content_type": ContentType.SPEC,
            "embedding": [0.8, 0.6],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "freshness_ts": fresh_ts,
                "truth_rank": 0.9,
                "embedding_degraded": False
            }
        },
        {
            "text": "Feature implementation notes",
            "path": "doc/specs/feat.md",
            "content_type": ContentType.SPEC,
            "embedding": [0.8, 0.6],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "freshness_ts": stale_ts,
                "truth_rank": 0.1,
                "embedding_degraded": False
            }
        }
    ]
    
    req = RerankRequest(
        query="Feature notes",
        candidates=candidates,
        top_k=2,
        content_type=ContentType.SPEC
    )
    
    resp = HybridReranker.rerank(
        request=req,
        query_vector=[0.8, 0.6],
        query_vector_space="text_fast_bge_small_384"
    )
    
    ranked = resp.ranked_candidates
    # Both candidates have identical text, path, and vector, but first has higher freshness and truth_rank
    first = ranked[0]
    second = ranked[1]
    
    assert first["metrics"]["freshness"] == 0.20
    assert second["metrics"]["freshness"] == 0.0
    
    assert first["metrics"]["truth_rank"] > second["metrics"]["truth_rank"]
    assert first["score"] > second["score"]

def test_dynamic_degradation_signaling():
    """Verifica que el estado de degraded se determine dinámicamente basado en la validez del vector space."""
    candidates_real = [
        {
            "text": "Active component",
            "path": "layers/l2_brain/active.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {"embedding_degraded": False}
        }
    ]
    
    candidates_fallback = [
        {
            "text": "Fallback component",
            "path": "layers/l2_brain/fallback.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "fallback_hash_384",
            "metadata": {"embedding_degraded": True}
        }
    ]
    
    req_real = RerankRequest(query="Active", candidates=candidates_real, top_k=1)
    req_fallback = RerankRequest(query="Fallback", candidates=candidates_fallback, top_k=1)
    
    # Case A: Real TEXT_FAST spaces compared -> degraded is False!
    resp_real = HybridReranker.rerank(
        request=req_real,
        query_vector=[1.0, 0.0],
        query_vector_space="text_fast_bge_small_384"
    )
    assert resp_real.degraded is False
    assert resp_real.reason == ""
    
    # Case B: Fallback query vector space compared -> degraded is True!
    resp_fallback = HybridReranker.rerank(
        request=req_fallback,
        query_vector=[1.0, 0.0],
        query_vector_space="fallback_hash_384"
    )
    assert resp_fallback.degraded is True
    assert "ML cross-encoder not configured" in resp_fallback.reason
