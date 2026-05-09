import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from local_reasoning import DeterministicReasoningProvider, LocalReasoningService


def test_deterministic_rerank_prefers_relevant_low_risk_candidates():
    service = LocalReasoningService(provider=DeterministicReasoningProvider())
    candidates = [
        {
            "id": "local.delete_everything",
            "text": "delete files permanently",
            "score": 0.92,
            "side_effect_level": "destructive",
        },
        {
            "id": "local.knowledge_search_context",
            "text": "search context and retrieve relevant knowledge for a task",
            "score": 0.55,
            "side_effect_level": "read",
        },
    ]

    result = service.reasoned_rerank(
        goal="retrieve relevant context for a task",
        candidates=candidates,
        max_selected=1,
    )

    assert result["provider_status"] == "deterministic"
    assert result["ranked"][0]["id"] == "local.knowledge_search_context"
    assert result["ranked"][0]["risk"] == "low"
    assert "why" in result["ranked"][0]


def test_context_shaper_returns_compact_cloud_agent_packet():
    service = LocalReasoningService(provider=DeterministicReasoningProvider())
    ranked = [
        {
            "id": "local.knowledge_search_context",
            "score": 0.8,
            "why": "retrieves relevant project context",
            "evidence_refs": ["memory://abc"],
        }
    ]

    packet = service.context_shaper(
        goal="Improve tool selection before cloud agent execution",
        ranked=ranked,
        token_budget=120,
        cloud_agent="codex",
    )

    assert packet["selected_tools"] == ["local.knowledge_search_context"]
    assert packet["task_brief"]
    assert packet["estimated_tokens"] <= 120
    assert packet["evidence_bundle"] == ["memory://abc"]


def test_context_shaper_caps_provider_estimated_tokens_to_budget():
    class OverBudgetProvider:
        name = "over_budget"

        def complete_json(self, task, payload):
            from local_reasoning import ReasoningResult

            return ReasoningResult(
                provider=self.name,
                status="ok",
                data={
                    "task_brief": payload["goal"],
                    "selected_tools": ["local.knowledge_search_context"],
                    "evidence_bundle": [],
                    "open_unknowns": [],
                    "execution_hint": "ok",
                    "estimated_tokens": 9999,
                },
            )

    service = LocalReasoningService(provider=OverBudgetProvider())

    packet = service.context_shaper("retrieve context", [], token_budget=50)

    assert packet["estimated_tokens"] <= 50


def test_deterministic_rerank_allows_relevant_write_tool_when_goal_requires_persistence():
    service = LocalReasoningService(provider=DeterministicReasoningProvider())
    candidates = [
        {
            "id": "local.knowledge_search_context",
            "text": "search context and retrieve knowledge",
            "score": 0.6,
            "side_effect_level": "read",
        },
        {
            "id": "local.selection_feedback",
            "text": "persist structured selection feedback in 4D-TES",
            "score": 0.5,
            "side_effect_level": "write",
        },
    ]

    result = service.reasoned_rerank(
        goal="persist a validated lesson in 4D-TES after a task succeeds",
        candidates=candidates,
        max_selected=1,
    )

    assert result["ranked"][0]["id"] == "local.selection_feedback"
    assert result["ranked"][0]["risk"] == "medium"


def test_provider_result_tolerates_model_json_wrapped_in_text():
    provider = DeterministicReasoningProvider()

    parsed = provider.parse_json_response('Result:\n```json\n{"ranked": [{"id": "a"}]}\n```')

    assert parsed == {"ranked": [{"id": "a"}]}
