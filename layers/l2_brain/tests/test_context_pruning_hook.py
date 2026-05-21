import pytest
from unittest.mock import MagicMock
from layers.l2_brain.metacognition.context_pruning import (
    ContextPruningHook,
    MemoryContextItem,
    _compute_relevance,
    _compute_importance,
    _compute_freshness,
    _rir_score,
    _cosine_similarity,
    _compress_text,
)
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame
from layers.l2_brain.domain.authority import AuthorityLevel


class TestRIRScoring:
    def test_cosine_similarity_identical(self):
        v = [1.0, 0.0, 0.0]
        assert _cosine_similarity(v, v) == 1.0

    def test_cosine_similarity_orthogonal(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == 0.0

    def test_cosine_similarity_empty(self):
        assert _cosine_similarity([], []) == 0.0
        assert _cosine_similarity([1.0], []) == 0.0

    def test_compute_relevance_no_embedding(self):
        assert _compute_relevance([1.0], None) == 0.3

    def test_compute_importance_human(self):
        score = _compute_importance("HUMAN", "CRYSTALLIZATION", 3)
        assert score > 1.0

    def test_compute_importance_agent_observation(self):
        score = _compute_importance("AGENT", "OBSERVATION", 0)
        assert score == pytest.approx(0.4, abs=0.01)

    def test_compute_freshness_same(self):
        assert _compute_freshness(100, 100) == 1.0

    def test_compute_freshness_old(self):
        assert _compute_freshness(0, 200) < 0.2

    def test_rir_score_formula(self):
        score = _rir_score(0.6, 0.7, 0.8)
        expected = 0.5 * 0.6 + 0.3 * 0.7 + 0.2 * 0.8
        assert score == pytest.approx(expected, abs=0.01)

    def test_compress_text_short(self):
        assert _compress_text("hello world", 100) == "hello world"

    def test_compress_text_long(self):
        text = "a" * 200
        result = _compress_text(text, 50)
        assert len(result) == 52


@pytest.mark.asyncio
class TestContextPruningHookNoMemory:
    async def test_empty_frame_noop(self):
        hook = ContextPruningHook(max_context_tokens=1024)
        frame = MetacognitiveFrame(session_id="test", raw_user_input="hello")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("total_input_tokens", 0) == 0
        assert pruned.get("items") == []

    async def test_hook_failure_does_not_crash_frame(self):
        hook = ContextPruningHook(max_context_tokens=1024)
        frame = MetacognitiveFrame(session_id="test", raw_user_input="hello")
        frame.telemetry["context_items"] = [{"invalid": "data"}]
        result = await hook.run(frame)
        assert "pruned_context" in result.telemetry

    async def test_graceful_degradation_no_embedder(self):
        hook = ContextPruningHook(max_context_tokens=1024, query_embedder=None)
        items = [
            MemoryContextItem(
                ref="mem1",
                content="important strategic decision about architecture",
                authority="HUMAN",
                intent_i="CRYSTALLIZATION",
                lamport_t=100,
                embedding=None,
                proof_evidence=5,
            )
        ]
        hook.memory_resolver = lambda q: items
        frame = MetacognitiveFrame(session_id="test", raw_user_input="strategy")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("items_preserved", 0) >= 1


@pytest.mark.asyncio
class TestContextPruningHookWithMemory:
    async def test_preserves_high_rir_items(self):
        hook = ContextPruningHook(max_context_tokens=4096)
        items = [
            MemoryContextItem(
                ref="mem_high",
                content="critical architectural decision with long term implications",
                authority="HUMAN",
                intent_i="CRYSTALLIZATION",
                lamport_t=200,
                embedding=[0.9, 0.1, 0.1],
                proof_evidence=5,
            ),
            MemoryContextItem(
                ref="mem_low",
                content="unimportant log entry from long ago",
                authority="AGENT",
                intent_i="OBSERVATION",
                lamport_t=10,
                embedding=[0.1, 0.9, 0.1],
                proof_evidence=0,
            ),
        ]
        hook.memory_resolver = lambda q: items

        frame = MetacognitiveFrame(
            session_id="test",
            raw_user_input="architecture decision",
            refined_intent="OBJECTIVE_INQUIRY",
        )
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        refs = [i["ref"] for i in pruned.get("items", [])]
        assert "mem_high" in refs
        assert len(refs) >= 1

    async def test_token_budget_enforcement(self):
        hook = ContextPruningHook(max_context_tokens=50)
        items = [
            MemoryContextItem(
                ref=f"mem_{i}",
                content="x" * 500,
                authority="AGENT",
                intent_i="OBSERVATION",
                lamport_t=100 - i,
                embedding=[0.5] * 4,
                proof_evidence=0,
            )
            for i in range(20)
        ]
        hook.memory_resolver = lambda q: items

        frame = MetacognitiveFrame(session_id="test", raw_user_input="test")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("total_output_tokens", 0) <= 50

    async def test_memory_resolver_accepts_dicts(self):
        hook = ContextPruningHook(max_context_tokens=4096)
        raw_dicts = [
            {
                "ref": "dict1",
                "content": "strategic analysis result",
                "authority": "ARCHITECT",
                "intent_i": "RESOLUTION",
                "lamport_t": 150,
                "embedding": [0.8, 0.2],
                "proof_evidence": 3,
            }
        ]
        hook.memory_resolver = lambda q: raw_dicts

        frame = MetacognitiveFrame(session_id="test", raw_user_input="strategy")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("items_preserved", 0) >= 1

    async def test_low_rir_items_dropped_before_high(self):
        hook = ContextPruningHook(max_context_tokens=4096)
        items = [
            MemoryContextItem(
                ref="high_value",
                content="critical design document about system architecture",
                authority="HUMAN",
                intent_i="CRYSTALLIZATION",
                lamport_t=200,
                embedding=[0.9] * 4,
                proof_evidence=5,
            ),
            MemoryContextItem(
                ref="low_noise",
                content="random unimportant log",
                authority="AGENT",
                intent_i="OBSERVATION",
                lamport_t=1,
                embedding=[0.01] * 4,
                proof_evidence=0,
            ),
        ]
        hook.memory_resolver = lambda q: items

        frame = MetacognitiveFrame(
            session_id="test", raw_user_input="architecture design"
        )
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        refs = [i["ref"] for i in pruned.get("items", [])]
        assert "high_value" in refs
        assert "low_noise" not in refs

    async def test_no_resolver_uses_telemetry_items(self):
        hook = ContextPruningHook(max_context_tokens=4096, query_embedder=None)
        frame = MetacognitiveFrame(session_id="test", raw_user_input="hello")
        frame.telemetry["context_items"] = [
            {
                "ref": "tele_item_1",
                "content": "data from previous hook",
                "authority": "ENGINEER",
                "intent_i": "MUTATION",
                "lamport_t": 50,
                "embedding": None,
                "proof_evidence": 1,
            }
        ]
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("items_preserved", 0) + pruned.get("items_compressed", 0) >= 1
