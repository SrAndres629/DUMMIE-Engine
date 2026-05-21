import logging
import math
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, List, Optional

from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.context_pruning")

AUTHORITY_IMPORTANCE = {
    "HUMAN": 1.0,
    "OVERSEER": 0.9,
    "ARCHITECT": 0.8,
    "ENGINEER": 0.7,
    "AGENT": 0.5,
}

INTENT_BONUS = {
    "CRYSTALLIZATION": 0.15,
    "RESOLUTION": 0.10,
    "AUDIT": 0.05,
    "MUTATION": 0.00,
    "FABRICATION": -0.05,
    "OBSERVATION": -0.10,
}

RIR_ALPHA = 0.5
RIR_BETA = 0.3
RIR_GAMMA = 0.2

DROP_THRESHOLD = 0.15
COMPRESS_THRESHOLD = 0.35
COMPRESS_MAX_CHARS = 120
PRESERVE_MAX_CHARS = 1024
LAMPORT_DECAY_CONSTANT = 100.0
PROOF_EVIDENCE_MAX = 5.0

DEFAULT_MAX_TOKENS = 4096


@dataclass
class MemoryContextItem:
    ref: str
    content: str
    authority: str
    intent_i: str
    lamport_t: int
    embedding: Optional[List[float]] = None
    proof_evidence: int = 0


@dataclass
class PrunedContextItem:
    ref: str
    content: str
    rir_score: float
    relevance: float
    importance: float
    freshness: float
    decision: str
    estimated_tokens: int
    reason: str = ""


@dataclass
class PruningResult:
    items: List[PrunedContextItem] = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    rir_scores: List[float] = field(default_factory=list)
    items_preserved: int = 0
    items_compressed: int = 0
    items_dropped: int = 0
    empty_after_pruning: bool = False
    budget_exhausted: bool = False


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _compress_text(text: str, max_chars: int) -> str:
    t = " ".join(text.split())
    if len(t) <= max_chars:
        return t
    return t[: max(1, max_chars - 1)] + "..."


def _compute_relevance(
    query_embedding: List[float], item_embedding: Optional[List[float]]
) -> float:
    if not item_embedding:
        return 0.3
    return _cosine_similarity(query_embedding, item_embedding)


def _compute_importance(authority: str, intent_i: str, proof_evidence: int) -> float:
    base = AUTHORITY_IMPORTANCE.get(authority.upper(), 0.3)
    bonus = INTENT_BONUS.get(intent_i.upper(), 0.0)
    proof_score = min(1.0, proof_evidence / PROOF_EVIDENCE_MAX)
    return base + bonus + (proof_score * 0.1)


def _compute_freshness(lamport_t: int, max_lamport: int) -> float:
    if max_lamport <= 0:
        return 0.5
    delta = max_lamport - lamport_t
    return math.exp(-delta / LAMPORT_DECAY_CONSTANT)


def _rir_score(relevance: float, importance: float, freshness: float) -> float:
    return RIR_ALPHA * relevance + RIR_BETA * importance + RIR_GAMMA * freshness


class ContextPruningHook:
    def __init__(
        self,
        max_context_tokens: Optional[int] = None,
        memory_resolver: Optional[Callable] = None,
        query_embedder: Optional[Callable] = None,
    ):
        self.max_context_tokens = (
            max_context_tokens
            if max_context_tokens is not None
            else int(os.getenv("DUMMIE_MAX_CONTEXT_TOKENS", str(DEFAULT_MAX_TOKENS)))
        )
        self.memory_resolver = memory_resolver
        self.query_embedder = query_embedder

        if self.query_embedder is None:
            try:
                from layers.l2_brain.embedding_mesh.specialized_providers import (
                    generate_vector,
                )

                self.query_embedder = generate_vector
            except ImportError:
                logger.warning(
                    "generate_vector not available, relevance scoring will use heuristic defaults"
                )

    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        try:
            items = await self._resolve_items(frame)
            if not items:
                frame.telemetry["pruned_context"] = self._empty_result()
                return frame

            query = frame.refined_intent or frame.raw_user_input

            query_embedding = None
            if self.query_embedder:
                try:
                    query_embedding = self.query_embedder(query)
                except Exception as e:
                    logger.warning(f"query embedding failed: {e}")

            max_lamport = max((item.lamport_t for item in items), default=0)

            scored: list = []
            for item in items:
                relevance = _compute_relevance(query_embedding or [], item.embedding)
                importance = _compute_importance(
                    item.authority, item.intent_i, item.proof_evidence
                )
                freshness = _compute_freshness(item.lamport_t, max_lamport)
                rir = _rir_score(relevance, importance, freshness)
                scored.append((rir, item, relevance, importance, freshness))

            scored.sort(key=lambda x: x[0], reverse=True)

            result = PruningResult()
            budget_remaining = self.max_context_tokens

            for scored_entry in scored:
                rir, item, relevance, importance, freshness = scored_entry
                input_tokens = _estimate_tokens(item.content)
                result.total_input_tokens += input_tokens

                if rir < DROP_THRESHOLD:
                    result.items_dropped += 1
                    continue

                if rir < COMPRESS_THRESHOLD:
                    compressed = _compress_text(item.content, COMPRESS_MAX_CHARS)
                    out_tokens = _estimate_tokens(compressed)
                    if out_tokens > budget_remaining and result.items:
                        result.budget_exhausted = True
                        result.items_dropped += 1
                        continue
                    budget_remaining -= out_tokens
                    result.items_compressed += 1
                    result.items.append(
                        PrunedContextItem(
                            ref=item.ref,
                            content=compressed,
                            rir_score=round(rir, 4),
                            relevance=round(relevance, 4),
                            importance=round(importance, 4),
                            freshness=round(freshness, 4),
                            decision="compress",
                            estimated_tokens=out_tokens,
                            reason="rir_below_compress_threshold",
                        )
                    )
                    continue

                preserved = _compress_text(item.content, PRESERVE_MAX_CHARS)
                out_tokens = _estimate_tokens(preserved)
                if out_tokens > budget_remaining and result.items:
                    result.budget_exhausted = True
                    result.items_dropped += 1
                    continue
                budget_remaining -= out_tokens
                result.items_preserved += 1
                result.items.append(
                    PrunedContextItem(
                        ref=item.ref,
                        content=preserved,
                        rir_score=round(rir, 4),
                        relevance=round(relevance, 4),
                        importance=round(importance, 4),
                        freshness=round(freshness, 4),
                        decision="preserve",
                        estimated_tokens=out_tokens,
                        reason="rir_above_preserve_threshold",
                    )
                )

            result.total_output_tokens = sum(i.estimated_tokens for i in result.items)
            result.rir_scores = [i.rir_score for i in result.items]
            result.empty_after_pruning = len(result.items) == 0

            frame.telemetry["pruned_context"] = {
                "items": [asdict(i) for i in result.items],
                "total_input_tokens": result.total_input_tokens,
                "total_output_tokens": result.total_output_tokens,
                "reduction_ratio": round(
                    (result.total_input_tokens - result.total_output_tokens)
                    / max(1, result.total_input_tokens),
                    4,
                ),
                "items_preserved": result.items_preserved,
                "items_compressed": result.items_compressed,
                "items_dropped": result.items_dropped,
                "empty_after_pruning": result.empty_after_pruning,
                "budget_exhausted": result.budget_exhausted,
                "max_context_tokens": self.max_context_tokens,
            }

            if result.total_input_tokens > self.max_context_tokens:
                logger.info(
                    f"Context pruned: {result.total_input_tokens}→{result.total_output_tokens} tokens "
                    f"({len(result.items)} items, {result.items_dropped} dropped)"
                )

        except Exception as e:
            logger.error(f"ContextPruningHook failed: {e}", exc_info=True)
            frame.telemetry["pruned_context"] = {
                **self._empty_result(),
                "error": str(e),
            }

        return frame

    async def _resolve_items(
        self, frame: MetacognitiveFrame
    ) -> List[MemoryContextItem]:
        if self.memory_resolver is not None:
            try:
                query = frame.refined_intent or frame.raw_user_input
                raw = self.memory_resolver(query)
                if hasattr(raw, "__await__"):
                    raw = await raw
                items = []
                for r in raw:
                    if isinstance(r, MemoryContextItem):
                        items.append(r)
                    elif isinstance(r, dict):
                        items.append(
                            MemoryContextItem(
                                ref=str(r.get("ref", "")),
                                content=str(r.get("content", "")),
                                authority=str(r.get("authority", "AGENT")),
                                intent_i=str(r.get("intent_i", "OBSERVATION")),
                                lamport_t=int(r.get("lamport_t", 0)),
                                embedding=r.get("embedding"),
                                proof_evidence=int(r.get("proof_evidence", 0)),
                            )
                        )
                    else:
                        try:
                            items.append(
                                MemoryContextItem(
                                    ref=getattr(r, "causal_hash", str(id(r))),
                                    content=getattr(r, "payload", str(r)),
                                    authority=getattr(r, "authority_a", "AGENT"),
                                    intent_i=getattr(r, "intent_i", "OBSERVATION"),
                                    lamport_t=getattr(r, "lamport_t", 0),
                                    embedding=getattr(r, "embedding", None),
                                    proof_evidence=getattr(r, "proof_evidence", 0),
                                )
                            )
                        except Exception:
                            logger.warning(
                                f"skipping unresolvable memory item: {type(r)}"
                            )
                return items
            except Exception as e:
                logger.warning(f"memory_resolver failed: {e}")

        raw_items = frame.telemetry.get("context_items") or frame.telemetry.get(
            "memory_items"
        )
        if raw_items:
            return [
                MemoryContextItem(
                    ref=str(i.get("ref", "")),
                    content=str(i.get("content", i.get("payload", ""))),
                    authority=str(i.get("authority", i.get("authority_a", "AGENT"))),
                    intent_i=str(i.get("intent_i", "OBSERVATION")),
                    lamport_t=int(i.get("lamport_t", 0)),
                    embedding=i.get("embedding"),
                    proof_evidence=int(i.get("proof_evidence", 0)),
                )
                for i in raw_items
            ]

        return []

    @staticmethod
    def _empty_result() -> dict:
        return {
            "items": [],
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "reduction_ratio": 0.0,
            "items_preserved": 0,
            "items_compressed": 0,
            "items_dropped": 0,
            "empty_after_pruning": False,
            "budget_exhausted": False,
            "max_context_tokens": DEFAULT_MAX_TOKENS,
        }
