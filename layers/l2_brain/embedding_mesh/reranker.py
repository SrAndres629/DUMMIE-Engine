# Spec Reference: 192_embedding_mesh_foundation
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Tuple

from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    RerankRequest,
    RerankResponse,
    vector_spaces_compatible,
)


class HybridReranker:
    """
    Deterministic reranker for offline-safe hardening workflows.

    This reranker is intentionally heuristic. It marks results as degraded
    because no ML cross-encoder is active in this phase.
    """

    @staticmethod
    def rerank(
        request: RerankRequest,
        query_vector: List[float] | None = None,
        query_vector_space: str | None = None,
        bypass: bool = False,
    ) -> RerankResponse:
        import os
        bypass_active = bypass or os.getenv("DUMMIE_RERANK_BYPASS", "0").strip() == "1"

        query_tokens = set(_tokens(request.query))
        ranked: List[Dict[str, Any]] = []
        has_real_candidate = False

        weights = {
            "vector_similarity": 0.35,
            "token_overlap": 0.30,
            "path_overlap": 0.15,
            "contextual_boost": 0.10,
            "recency_freshness": 0.05,
            "importance_truth_rank": 0.05,
        }

        for candidate in request.candidates:
            cand_diagnostics = {}
            try:
                text, path, cand_type, embedding, cand_space, metadata = _extract_candidate_fields(candidate)
            except Exception as e:
                text, path, cand_type, embedding, cand_space, metadata = "", "", ContentType.UNKNOWN, [], None, {}
                cand_diagnostics["extract_error"] = str(e)

            text_tokens = set(_tokens(text))

            if path and isinstance(path, str):
                path_tokens = set(_tokens(path))
            else:
                path_tokens = set()
                cand_diagnostics["path_missing_or_invalid"] = True

            # Component 1: token_overlap (normalized)
            overlap_score = _ratio(len(query_tokens.intersection(text_tokens)), len(query_tokens))
            overlap_norm = max(0.0, min(1.0, overlap_score))

            # Component 2: path_overlap (normalized)
            path_score = _ratio(len(query_tokens.intersection(path_tokens)), len(query_tokens))
            path_norm = max(0.0, min(1.0, path_score))

            # Component 3: vector_similarity (normalized, compatible check)
            vector_score = 0.0
            vector_space_compat = False
            if query_vector and embedding:
                try:
                    vector_space_compat = vector_spaces_compatible(query_vector_space, cand_space)
                    if vector_space_compat:
                        vector_score = _vector_similarity_if_compatible(
                            query_vector=query_vector,
                            candidate_vector=embedding,
                            query_space=query_vector_space,
                            candidate_space=cand_space,
                        )
                except Exception as e:
                    cand_diagnostics["vector_error"] = str(e)

            vector_norm = max(0.0, min(1.0, vector_score))

            # Component 4: contextual_boost (normalized)
            boost = 0.0
            if isinstance(request.query, str):
                try:
                    boost = _contextual_boost(request.query, cand_type, path, metadata)
                except Exception as e:
                    cand_diagnostics["boost_error"] = str(e)
            boost_norm = max(0.0, min(1.0, boost / 0.50))  # normalize to 1.0 based on 0.50 cap

            # Component 5: recency_freshness (normalized)
            freshness = 0.0
            try:
                freshness = _freshness_score(metadata)
            except Exception as e:
                cand_diagnostics["freshness_error"] = str(e)
            freshness_norm = max(0.0, min(1.0, freshness / 0.20))  # normalize to 1.0 based on 0.20 max

            # Component 6: importance_truth_rank (normalized)
            truth_rank = 0.0
            try:
                truth_rank = _truth_rank_score(metadata)
            except Exception as e:
                cand_diagnostics["truth_rank_error"] = str(e)
            truth_rank_norm = max(0.0, min(1.0, truth_rank / 0.20))  # normalize to 1.0 based on 0.20 max

            # Penalty logic
            penalty = 0.0
            try:
                penalty = _classification_penalty(path, metadata)
            except Exception as e:
                cand_diagnostics["penalty_error"] = str(e)

            # Score logic
            if bypass_active:
                final_score = vector_norm
            else:
                final_score = (
                    vector_norm * weights["vector_similarity"]
                    + overlap_norm * weights["token_overlap"]
                    + path_norm * weights["path_overlap"]
                    + boost_norm * weights["contextual_boost"]
                    + freshness_norm * weights["recency_freshness"]
                    + truth_rank_norm * weights["importance_truth_rank"]
                    - penalty
                )

            if math.isnan(final_score) or math.isinf(final_score):
                final_score = 0.0
                cand_diagnostics["math_error"] = "Score is NaN or inf"

            final_score = max(0.0, min(1.0, final_score))

            is_candidate_degraded = False
            if isinstance(metadata, dict):
                is_candidate_degraded = metadata.get("embedding_degraded", False)
            else:
                is_candidate_degraded = getattr(metadata, "embedding_degraded", False)

            if cand_space == "text_fast_bge_small_384" and not is_candidate_degraded:
                has_real_candidate = True

            ranked.append(
                {
                    "candidate": candidate,
                    "score": round(final_score, 4),
                    "metrics": {
                        "overlap": round(overlap_score, 4),
                        "path": round(path_score, 4),
                        "vector": round(vector_score, 4),
                        "boost": round(boost, 4),
                        "freshness": round(freshness, 4),
                        "truth_rank": round(truth_rank, 4),
                        "penalty": round(penalty, 4),
                    },
                    "normalized_metrics": {
                        "vector_similarity": round(vector_norm, 4),
                        "token_overlap": round(overlap_norm, 4),
                        "path_overlap": round(path_norm, 4),
                        "contextual_boost": round(boost_norm, 4),
                        "recency_freshness": round(freshness_norm, 4),
                        "importance_truth_rank": round(truth_rank_norm, 4),
                        "penalty": round(penalty, 4),
                    },
                    "vector_space_compatible": vector_space_compat,
                    "diagnostics": cand_diagnostics,
                }
            )

        is_query_space_real = (
            query_vector_space == "text_fast_bge_small_384"
            and query_vector is not None
        )
        semantic_input_degraded = not (is_query_space_real and has_real_candidate)
        reranker_engine_degraded = True
        degraded = semantic_input_degraded or reranker_engine_degraded

        if bypass_active:
            ranking_mode = "bypass_vector_similarity"
            degraded = True
            reason = "Rollback / bypass active: ordered purely by raw vector similarity."
        elif not semantic_input_degraded:
            ranking_mode = "hybrid_real_embeddings"
            reason = "Offline deterministic hybrid+ rerank active using real local embeddings."
        else:
            ranking_mode = "hybrid_deterministic_fallback"
            reason = "ML cross-encoder not configured; operating under offline deterministic hash projection fallback."

        ranked.sort(key=lambda row: row["score"], reverse=True)

        response_diagnostics = {
            "bypass_active": bypass_active,
            "has_real_candidate": has_real_candidate,
            "is_query_space_real": is_query_space_real,
            "total_candidates": len(ranked),
        }
        return RerankResponse(
            ranked_candidates=ranked[: request.top_k],
            model_used="deterministic-hybrid-reranker",
            degraded=degraded,
            reason=reason,
            ranking_mode=ranking_mode,
            semantic_input_degraded=semantic_input_degraded,
            reranker_engine_degraded=reranker_engine_degraded,
            vector_space=query_vector_space,
            weights=weights,
            diagnostics=response_diagnostics,
        )


def _tokens(text: str) -> Iterable[str]:
    return re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())


def _extract_candidate_fields(candidate: Any) -> Tuple[str, str, ContentType, List[float], str | None, Dict[str, Any]]:
    if isinstance(candidate, dict):
        text = candidate.get("content") or candidate.get("text") or ""
        path = candidate.get("path") or ""
        content_type = candidate.get("content_type", ContentType.UNKNOWN)
        embedding = candidate.get("embedding") or []
        vector_space = candidate.get("vector_space")
        metadata = candidate.get("metadata") or {}
        return text, path, content_type, embedding, vector_space, metadata

    if hasattr(candidate, "__dict__"):
        text = getattr(candidate, "content", getattr(candidate, "text", ""))
        path = getattr(candidate, "path", "")
        content_type = getattr(candidate, "content_type", ContentType.UNKNOWN)
        embedding = getattr(candidate, "embedding", [])
        vector_space = getattr(candidate, "vector_space", None)
        metadata = getattr(candidate, "metadata", {}) or {}
        return text, path, content_type, embedding, vector_space, metadata

    return str(candidate), "", ContentType.UNKNOWN, [], None, {}


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _vector_similarity_if_compatible(
    query_vector: List[float] | None,
    candidate_vector: List[float] | None,
    query_space: str | None,
    candidate_space: str | None,
) -> float:
    if not query_vector or not candidate_vector:
        return 0.0
    if not vector_spaces_compatible(query_space, candidate_space):
        return 0.0
    if len(query_vector) != len(candidate_vector):
        return 0.0

    dot = sum(a * b for a, b in zip(query_vector, candidate_vector))
    query_norm = math.sqrt(sum(a * a for a in query_vector))
    cand_norm = math.sqrt(sum(b * b for b in candidate_vector))
    if query_norm == 0.0 or cand_norm == 0.0:
        return 0.0
    similarity = dot / (query_norm * cand_norm)
    return max(0.0, min(1.0, similarity))


def _contextual_boost(query: str, content_type: ContentType, path: str, metadata: Dict[str, Any]) -> float:
    query_lower = query.lower()
    path_lower = (path or "").lower()
    boost = 0.0

    if "spec" in query_lower and content_type == ContentType.SPEC:
        boost += 0.25
    if "test" in query_lower and content_type == ContentType.TEST:
        boost += 0.25
    if "module" in query_lower and content_type == ContentType.CODE:
        boost += 0.20
    if "report" in query_lower and "report" in path_lower:
        boost += 0.15
    if metadata.get("is_direct_match"):
        boost += 0.20

    return min(boost, 0.50)


def _classification_penalty(path: str, metadata: Dict[str, Any]) -> float:
    classification = (metadata.get("classification") or "").upper()
    path_lower = (path or "").lower()
    penalty = 0.0

    if classification == "LEGACY" or "legacy" in path_lower:
        penalty += 0.40
    if classification == "GENERATED" or "generated" in path_lower or "_pb2.py" in path_lower:
        penalty += 0.20
    if classification == "SHADOW_CANDIDATE":
        penalty += 0.25

    return penalty


def _freshness_score(metadata: Dict[str, Any]) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    raw = metadata.get("freshness_ts")
    if not raw or not isinstance(raw, str):
        return 0.0

    try:
        raw_norm = raw.replace("Z", "+00:00")
        freshness_dt = datetime.fromisoformat(raw_norm)
        
        if freshness_dt.tzinfo is None:
            freshness_dt = freshness_dt.replace(tzinfo=timezone.utc)
            
        tz = freshness_dt.tzinfo
        now = datetime.now(tz=tz)
        age_days = max(0.0, (now - freshness_dt).total_seconds() / 86400.0)
        
        if age_days <= 7:
            return 0.20
        if age_days <= 30:
            return 0.10
    except Exception:
        return 0.0
    return 0.0


def _truth_rank_score(metadata: Dict[str, Any]) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    score = metadata.get("truth_rank")
    if score is None:
        return 0.0
    try:
        score_f = float(score)
    except Exception:
        return 0.0
    return max(0.0, min(0.20, score_f * 0.20))
