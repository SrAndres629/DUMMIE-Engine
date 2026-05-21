"""Optimized ContextPruningHook with aggressive memory savings."""
import logging
import math
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, List, Optional

from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.context_pruning_optimized")

RIR_ALPHA = 0.6
RIR_BETA = 0.25
RIR_GAMMA = 0.15
DROP_THRESHOLD = 0.20
COMPRESS_THRESHOLD = 0.45
COMPRESS_MAX_CHARS = 80
PRESERVE_MAX_CHARS = 512
TOKEN_BUDGET_SIMPLE = 1024
TOKEN_BUDGET_NORMAL = 2048
TOKEN_BUDGET_COMPLEX = 4096
LAMPORT_DECAY_CONSTANT = 50.0

AUTHORITY_IMPORTANCE = {"HUMAN": 1.0, "OVERSEER": 0.9, "ARCHITECT": 0.8, "ENGINEER": 0.7, "AGENT": 0.5}
INTENT_BONUS = {"CRYSTALLIZATION": 0.15, "RESOLUTION": 0.10, "AUDIT": 0.05, "MUTATION": 0.0, "FABRICATION": -0.05, "OBSERVATION": -0.10}
PROOF_EVIDENCE_MAX = 5.0

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

def _cosine_similarity(a, b):
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0: return 0.0
    return dot / (na * nb)

def _estimate_tokens(text): return max(1, len(text) // 4)
def _compress_text(text, max_chars):
    t = " ".join(text.split())
    return t if len(t) <= max_chars else t[: max(1, max_chars - 1)] + "..."

def _compute_relevance(qe, ie):
    if not ie: return 0.25
    return _cosine_similarity(qe, ie)

def _compute_importance(authority, intent_i, proof):
    return AUTHORITY_IMPORTANCE.get(authority.upper(), 0.3) + INTENT_BONUS.get(intent_i.upper(), 0.0) + (min(1.0, proof / PROOF_EVIDENCE_MAX) * 0.1)

def _compute_freshness(lamport_t, max_lamport):
    if max_lamport <= 0: return 0.5
    return math.exp(-(max_lamport - lamport_t) / LAMPORT_DECAY_CONSTANT)

def _rir_score(relevance, importance, freshness):
    return RIR_ALPHA * relevance + RIR_BETA * importance + RIR_GAMMA * freshness

def _estimate_task_complexity(query):
    q = query.lower()
    if any(k in q for k in ["architect", "design", "migration", "refactor", "optimize", "deploy", "production"]): return "complex"
    if any(k in q for k in ["status", "hello", "hi", "help", "what", "list", "show"]): return "simple"
    return "normal"

def _get_token_budget(complexity):
    env = os.getenv("DUMMIE_MAX_CONTEXT_TOKENS")
    if env: return int(env)
    return {"simple": TOKEN_BUDGET_SIMPLE, "normal": TOKEN_BUDGET_NORMAL, "complex": TOKEN_BUDGET_COMPLEX}.get(complexity, TOKEN_BUDGET_NORMAL)

class OptimizedContextPruningHook:
    def __init__(self, memory_resolver=None, query_embedder=None):
        self.memory_resolver = memory_resolver
        self.query_embedder = query_embedder
        if self.query_embedder is None:
            try:
                from layers.l2_brain.embedding_mesh.specialized_providers import generate_vector
                self.query_embedder = generate_vector
            except ImportError:
                pass

    async def run(self, frame):
        try:
            items = await self._resolve_items(frame)
            if not items:
                frame.telemetry["pruned_context"] = self._empty_result()
                return frame
            query = frame.refined_intent or frame.raw_user_input
            complexity = _estimate_task_complexity(query)
            max_tokens = _get_token_budget(complexity)
            qe = None
            if self.query_embedder:
                try: qe = self.query_embedder(query)
                except: pass
            max_lamport = max((i.lamport_t for i in items), default=0)
            scored = []
            for item in items:
                rel = _compute_relevance(qe or [], item.embedding)
                imp = _compute_importance(item.authority, item.intent_i, item.proof_evidence)
                fresh = _compute_freshness(item.lamport_t, max_lamport)
                rir = _rir_score(rel, imp, fresh)
                scored.append((rir, item, rel, imp, fresh))
            scored.sort(key=lambda x: x[0], reverse=True)
            result_items = []
            budget = max_tokens
            in_tokens = 0
            preserved = compressed = dropped = 0
            for rir, item, rel, imp, fresh in scored:
                in_tokens += _estimate_tokens(item.content)
                if rir < DROP_THRESHOLD:
                    dropped += 1
                    continue
                if rir < COMPRESS_THRESHOLD:
                    text = _compress_text(item.content, COMPRESS_MAX_CHARS)
                    ot = _estimate_tokens(text)
                    if ot > budget and result_items:
                        dropped += 1
                        continue
                    budget -= ot
                    compressed += 1
                    result_items.append(PrunedContextItem(ref=item.ref, content=text, rir_score=round(rir, 4), relevance=round(rel, 4), importance=round(imp, 4), freshness=round(fresh, 4), decision="compress", estimated_tokens=ot, reason="compressed"))
                    continue
                text = _compress_text(item.content, PRESERVE_MAX_CHARS)
                ot = _estimate_tokens(text)
                if ot > budget and result_items:
                    dropped += 1
                    continue
                budget -= ot
                preserved += 1
                result_items.append(PrunedContextItem(ref=item.ref, content=text, rir_score=round(rir, 4), relevance=round(rel, 4), importance=round(imp, 4), freshness=round(fresh, 4), decision="preserve", estimated_tokens=ot, reason="preserved"))
            out_tokens = sum(i.estimated_tokens for i in result_items)
            frame.telemetry["pruned_context"] = {"items": [asdict(i) for i in result_items], "total_input_tokens": in_tokens, "total_output_tokens": out_tokens, "reduction_ratio": round((in_tokens - out_tokens) / max(1, in_tokens), 4), "items_preserved": preserved, "items_compressed": compressed, "items_dropped": dropped, "empty_after_pruning": len(result_items) == 0, "budget_exhausted": budget <= 0, "max_context_tokens": max_tokens, "task_complexity": complexity}
        except Exception as e:
            logger.error(f"OptimizedContextPruningHook failed: {e}")
            frame.telemetry["pruned_context"] = {**self._empty_result(), "error": str(e)}
        return frame

    async def _resolve_items(self, frame):
        if self.memory_resolver:
            try:
                raw = self.memory_resolver(frame.refined_intent or frame.raw_user_input)
                if hasattr(raw, "__await__"): raw = await raw
                items = []
                for r in raw:
                    if isinstance(r, MemoryContextItem): items.append(r)
                    elif isinstance(r, dict): items.append(MemoryContextItem(ref=str(r.get("ref","")), content=str(r.get("content","")), authority=str(r.get("authority","AGENT")), intent_i=str(r.get("intent_i","OBSERVATION")), lamport_t=int(r.get("lamport_t",0)), embedding=r.get("embedding"), proof_evidence=int(r.get("proof_evidence",0))))
                return items
            except: pass
        raw_items = frame.telemetry.get("context_items") or frame.telemetry.get("memory_items")
        if raw_items:
            return [MemoryContextItem(ref=str(i.get("ref","")), content=str(i.get("content",i.get("payload",""))), authority=str(i.get("authority",i.get("authority_a","AGENT"))), intent_i=str(i.get("intent_i","OBSERVATION")), lamport_t=int(i.get("lamport_t",0)), embedding=i.get("embedding"), proof_evidence=int(i.get("proof_evidence",0))) for i in raw_items]
        return []

    @staticmethod
    def _empty_result():
        return {"items": [], "total_input_tokens": 0, "total_output_tokens": 0, "reduction_ratio": 0.0, "items_preserved": 0, "items_compressed": 0, "items_dropped": 0, "empty_after_pruning": False, "budget_exhausted": False, "max_context_tokens": TOKEN_BUDGET_NORMAL, "task_complexity": "unknown"}
