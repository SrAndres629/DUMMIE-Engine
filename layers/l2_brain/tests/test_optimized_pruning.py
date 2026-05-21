import pytest
from layers.l2_brain.metacognition.context_pruning_optimized import (
    OptimizedContextPruningHook,
    MemoryContextItem,
    _compute_relevance,
    _estimate_task_complexity,
    _get_token_budget,
    DROP_THRESHOLD,
    COMPRESS_THRESHOLD,
    TOKEN_BUDGET_SIMPLE,
    TOKEN_BUDGET_NORMAL,
    TOKEN_BUDGET_COMPLEX,
)
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame


class TestOptimizedThresholds:
    def test_drop_threshold_higher(self):
        assert DROP_THRESHOLD == 0.20

    def test_compress_threshold_higher(self):
        assert COMPRESS_THRESHOLD == 0.45


class TestTaskComplexity:
    def test_simple_task(self):
        assert _estimate_task_complexity("hello") == "simple"
        assert _estimate_task_complexity("status") == "simple"

    def test_complex_task(self):
        assert _estimate_task_complexity("architect migration") == "complex"

    def test_normal_task(self):
        assert _estimate_task_complexity("search for files") == "normal"

    def test_token_budget_simple(self):
        assert _get_token_budget("simple") == TOKEN_BUDGET_SIMPLE
        assert TOKEN_BUDGET_SIMPLE == 1024

    def test_token_budget_normal(self):
        assert _get_token_budget("normal") == TOKEN_BUDGET_NORMAL
        assert TOKEN_BUDGET_NORMAL == 2048

    def test_token_budget_complex(self):
        assert _get_token_budget("complex") == TOKEN_BUDGET_COMPLEX
        assert TOKEN_BUDGET_COMPLEX == 4096


@pytest.mark.asyncio
class TestOptimizedHook:
    async def test_simple_task_low_budget(self):
        hook = OptimizedContextPruningHook(query_embedder=None)
        items = [
            MemoryContextItem(
                ref="mem1", content="strategic decision",
                authority="HUMAN", intent_i="CRYSTALLIZATION", lamport_t=100,
                embedding=None, proof_evidence=5,
            ),
        ]
        hook.memory_resolver = lambda q: items
        frame = MetacognitiveFrame(session_id="test", raw_user_input="hello")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("task_complexity") == "simple"
        assert pruned.get("max_context_tokens") == 1024

    async def test_complex_task_high_budget(self):
        hook = OptimizedContextPruningHook(query_embedder=None)
        items = [
            MemoryContextItem(
                ref="mem1", content="architectural design",
                authority="ARCHITECT", intent_i="CRYSTALLIZATION", lamport_t=100,
                embedding=None, proof_evidence=5,
            ),
        ]
        hook.memory_resolver = lambda q: items
        frame = MetacognitiveFrame(session_id="test", raw_user_input="design migration architecture")
        result = await hook.run(frame)
        pruned = result.telemetry.get("pruned_context", {})
        assert pruned.get("task_complexity") == "complex"
        assert pruned.get("max_context_tokens") == 4096
