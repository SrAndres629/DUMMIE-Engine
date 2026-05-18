import math
import re
from datetime import datetime
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
    ) -> RerankResponse:
        query_tokens = set(_tokens(request.query))
        ranked: List[Dict[str, Any]] = []

        for candidate in request.candidates:
            text, path, cand_type, embedding, cand_space, metadata = _extract_candidate_fields(candidate)
            text_tokens = set(_tokens(text))
            path_tokens = set(_tokens(path))

            overlap_score = _ratio(len(query_tokens.intersection(text_tokens)), len(query_tokens))
            path_score = _ratio(len(query_tokens.intersection(path_tokens)), len(query_tokens))
            vector_score = _vector_similarity_if_compatible(
                query_vector=query_vector,
                candidate_vector=embedding,
                query_space=query_vector_space,
                candidate_space=cand_space,
            )
            boost = _contextual_boost(request.query, cand_type, path, metadata)
            penalty = _classification_penalty(path, metadata)
            freshness = _freshness_score(metadata)
            truth_rank = _truth_rank_score(metadata)

            final_score = (
                overlap_score * 0.30
                + path_score * 0.15
                + vector_score * 0.35
                + boost * 0.10
                + freshness * 0.05
                + truth_rank * 0.05
                - penalty
            )
            final_score = max(0.0, min(1.0, final_score))

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
                    "vector_space_compatible": vector_spaces_compatible(query_vector_space, cand_space),
                }
            )

        ranked.sort(key=lambda row: row["score"], reverse=True)
        return RerankResponse(
            ranked_candidates=ranked[: request.top_k],
            model_used="deterministic-hybrid-reranker",
            degraded=True,
            reason="ML cross-encoder not configured; hybrid deterministic rerank active",
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
    raw = metadata.get("freshness_ts")
    if not raw:
        return 0.0

    try:
        freshness_dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return 0.0

    age_days = max(0.0, (datetime.now(tz=freshness_dt.tzinfo) - freshness_dt).total_seconds() / 86400.0)
    if age_days <= 7:
        return 0.20
    if age_days <= 30:
        return 0.10
    return 0.0


def _truth_rank_score(metadata: Dict[str, Any]) -> float:
    score = metadata.get("truth_rank")
    if score is None:
        return 0.0
    try:
        score_f = float(score)
    except Exception:
        return 0.0
    return max(0.0, min(0.20, score_f * 0.20))
