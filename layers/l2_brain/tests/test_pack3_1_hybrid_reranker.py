# Regression test suite for Pack 3.1 - Hybrid Reranker Activation
import os
import math
from datetime import datetime, timezone, timedelta
from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    RerankRequest,
    RerankResponse,
    RerankMode,
)
from layers.l2_brain.embedding_mesh.reranker import HybridReranker

def test_weights_sum_to_one():
    """1. test_weights_sum_to_one: Verifica que la suma de pesos sea exactamente 1.0."""
    req = RerankRequest(
        query="test",
        candidates=[{"text": "candidate", "path": "test.py", "embedding": [1.0], "vector_space": "text_fast_bge_small_384"}],
        top_k=1
    )
    resp = HybridReranker.rerank(req, query_vector=[1.0], query_vector_space="text_fast_bge_small_384")
    assert resp.weights is not None
    total_weight = sum(resp.weights.values())
    assert abs(total_weight - 1.0) < 1e-9

def test_real_text_fast_vectors_set_semantic_input_not_degraded():
    """2. test_real_text_fast_vectors_set_semantic_input_not_degraded:
    Verifica que con embeddings reales el input no esté degradado, pero el motor y el global sí."""
    req = RerankRequest(
        query="core optimizer",
        candidates=[{
            "text": "Core module optimizer",
            "path": "layers/l2_brain/core.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {"embedding_degraded": False}
        }],
        top_k=1
    )
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    assert resp.semantic_input_degraded is False
    assert resp.reranker_engine_degraded is True
    assert resp.degraded is True  # degraded global because engine is hybrid deterministic
    assert resp.ranking_mode == RerankMode.HYBRID_REAL_EMBEDDINGS.value

def test_fallback_vectors_keep_response_degraded():
    """3. test_fallback_vectors_keep_response_degraded:
    Vectores fallback_hash_384 producen degraded=True en input y global."""
    req = RerankRequest(
        query="fallback",
        candidates=[{
            "text": "Fallback candidate",
            "path": "layers/l2_brain/fallback.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "fallback_hash_384",
            "metadata": {"embedding_degraded": True}
        }],
        top_k=1
    )
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="fallback_hash_384")
    assert resp.semantic_input_degraded is True
    assert resp.degraded is True
    assert resp.ranking_mode == RerankMode.HYBRID_DETERMINISTIC_FALLBACK.value

def test_vector_space_mismatch_is_degraded_and_does_not_crash():
    """4. test_vector_space_mismatch_is_degraded_and_does_not_crash:
    Mismatch de espacio vectorial entre query y candidatos se maneja sin crash."""
    req = RerankRequest(
        query="mismatch",
        candidates=[{
            "text": "Mismatch space candidate",
            "path": "layers/l2_brain/mismatch.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "fallback_hash_384",
            "metadata": {"embedding_degraded": True}
        }],
        top_k=1
    )
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    assert resp.semantic_input_degraded is True
    assert resp.degraded is True
    assert len(resp.ranked_candidates) == 1
    assert resp.ranked_candidates[0]["vector_space_compatible"] is False

def test_freshness_changes_ranking():
    """5. test_freshness_changes_ranking:
    Dos candidatos idénticos; el más reciente (freshness) gana."""
    now_utc = datetime.now(timezone.utc)
    fresh_ts = (now_utc - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    stale_ts = (now_utc - timedelta(days=60)).isoformat().replace("+00:00", "Z")

    candidates = [
        {
            "text": "Target info doc",
            "path": "doc/specs/info.md",
            "content_type": ContentType.SPEC,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "freshness_ts": stale_ts,
                "truth_rank": 0.5,
                "embedding_degraded": False
            }
        },
        {
            "text": "Target info doc",
            "path": "doc/specs/info.md",
            "content_type": ContentType.SPEC,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "freshness_ts": fresh_ts,
                "truth_rank": 0.5,
                "embedding_degraded": False
            }
        }
    ]

    req = RerankRequest(query="info doc", candidates=candidates, top_k=2)
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    
    assert len(resp.ranked_candidates) == 2
    # El primero debe ser el fresco
    assert resp.ranked_candidates[0]["candidate"]["metadata"]["freshness_ts"] == fresh_ts
    assert resp.ranked_candidates[0]["score"] > resp.ranked_candidates[1]["score"]

def test_truth_rank_changes_ranking():
    """6. test_truth_rank_changes_ranking:
    Truth rank mayor desplaza posición cuando la diferencia es notable."""
    candidates = [
        {
            "text": "Common module functionality",
            "path": "layers/l2_brain/common.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "truth_rank": 0.1,
                "embedding_degraded": False
            }
        },
        {
            "text": "Common module functionality",
            "path": "layers/l2_brain/common.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "truth_rank": 0.9,
                "embedding_degraded": False
            }
        }
    ]

    req = RerankRequest(query="Common module", candidates=candidates, top_k=2)
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    
    assert len(resp.ranked_candidates) == 2
    assert resp.ranked_candidates[0]["candidate"]["metadata"]["truth_rank"] == 0.9
    assert resp.ranked_candidates[0]["score"] > resp.ranked_candidates[1]["score"]

def test_corrupt_metadata_does_not_crash():
    """7. test_corrupt_metadata_does_not_crash:
    Metadata corrupta (fechas inválidas, truth_rank string, path None) no provoca crash."""
    candidates = [
        {
            "text": "Corrupt candidate",
            "path": None,
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {
                "freshness_ts": "garbage_date_string",
                "truth_rank": "high_rank",
                "embedding_degraded": False
            }
        }
    ]

    req = RerankRequest(query="Corrupt", candidates=candidates, top_k=1)
    # No debe lanzar excepción
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    assert len(resp.ranked_candidates) == 1
    assert resp.ranked_candidates[0]["score"] >= 0.0

def test_path_overlap_affects_score():
    """8. test_path_overlap_affects_score:
    Candidatos con tokens que coinciden con su path reciben más score."""
    candidates = [
        {
            "text": "Module functionality",
            "path": "layers/l2_brain/utility.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {}
        },
        {
            "text": "Module functionality",
            "path": "layers/l2_brain/optimizer.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {}
        }
    ]

    req = RerankRequest(query="optimizer module", candidates=candidates, top_k=2)
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384")
    
    assert len(resp.ranked_candidates) == 2
    # El optimizer.py debe ganar por coincidencia en path
    assert "optimizer.py" in resp.ranked_candidates[0]["candidate"]["path"]
    assert resp.ranked_candidates[0]["score"] > resp.ranked_candidates[1]["score"]

def test_bypass_mode_orders_by_vector_similarity():
    """9. test_bypass_mode_orders_by_vector_similarity:
    Bypass fuerza orden puramente vectorial, degraded=True y ranking_mode=bypass."""
    candidates = [
        {
            "text": "Target text match low vector",
            "path": "doc/specs/info.md",
            "content_type": ContentType.SPEC,
            "embedding": [0.1, 0.9],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {}
        },
        {
            "text": "No text match high vector",
            "path": "doc/specs/other.md",
            "content_type": ContentType.SPEC,
            "embedding": [1.0, 0.0],
            "vector_space": "text_fast_bge_small_384",
            "metadata": {}
        }
    ]

    req = RerankRequest(query="Target text match", candidates=candidates, top_k=2)
    
    # Activamos bypass programáticamente
    resp = HybridReranker.rerank(req, query_vector=[1.0, 0.0], query_vector_space="text_fast_bge_small_384", bypass=True)
    
    assert resp.ranking_mode == RerankMode.BYPASS_VECTOR_SIMILARITY.value
    assert resp.degraded is True
    assert "bypass" in resp.reason.lower()
    
    # En bypass, el de vector [1.0, 0.0] debe ganar ya que coincide exactamente con query_vector
    assert resp.ranked_candidates[0]["candidate"]["text"] == "No text match high vector"

def test_diagnostics_explain_component_scores():
    """10. test_diagnostics_explain_component_scores:
    Cada candidato contiene componentes e información de diagnóstico legible."""
    req = RerankRequest(
        query="test diagnostics",
        candidates=[{"text": "candidate", "path": "test.py", "embedding": [1.0], "vector_space": "text_fast_bge_small_384"}],
        top_k=1
    )
    resp = HybridReranker.rerank(req, query_vector=[1.0], query_vector_space="text_fast_bge_small_384")
    
    assert resp.diagnostics is not None
    assert resp.diagnostics["total_candidates"] == 1
    
    cand = resp.ranked_candidates[0]
    assert "normalized_metrics" in cand
    assert "vector_similarity" in cand["normalized_metrics"]
    assert "token_overlap" in cand["normalized_metrics"]
    assert "diagnostics" in cand
