import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools_impl.local_reasoning import LocalReasoningToolService


class FakeToolManager:
    def list_tools(self):
        return [
            SimpleNamespace(
                name="knowledge_search_context",
                description="Search context and retrieve knowledge",
                parameters={"properties": {"query": {"type": "string"}}},
            ),
            SimpleNamespace(
                name="crystallize",
                description="Persist validated knowledge in 4D-TES",
                parameters={"properties": {"payload": {"type": "string"}}},
            ),
        ]


class FakeInternalMCP:
    _tool_manager = FakeToolManager()


class FakeProxy:
    def __init__(self):
        self.servers = {
            "socraticode": {
                "profile": "code_search",
                "capability_class": "semantic_codebase",
                "rationale": "semantic codebase search",
            }
        }
        self.remote_tool_calls = 0

    async def get_tools_for_server(self, server_name):
        self.remote_tool_calls += 1
        return []


@pytest.mark.asyncio
async def test_semantic_recall_returns_mcp_candidates_without_side_effects():
    service = LocalReasoningToolService(
        proxy_manager=FakeProxy(),
        internal_mcp=FakeInternalMCP(),
        orchestrator=SimpleNamespace(event_store=None),
    )

    result = await service.semantic_recall(
        goal="retrieve project context",
        query="search context",
        top_k=2,
        sources=["mcp"],
    )

    assert result["provider_status"] == "ok"
    assert result["candidates"][0]["id"].startswith("local.")
    assert result["candidates"][0]["side_effect_level"] in {"read", "write", "external", "destructive"}
    assert service.proxy_manager.remote_tool_calls == 0


@pytest.mark.asyncio
async def test_semantic_recall_includes_remote_registry_without_starting_remote_tools():
    service = LocalReasoningToolService(
        proxy_manager=FakeProxy(),
        internal_mcp=FakeInternalMCP(),
        orchestrator=SimpleNamespace(event_store=None),
    )

    result = await service.semantic_recall(
        goal="semantic codebase search",
        query="socraticode search",
        top_k=5,
        sources=["mcp"],
    )

    assert any(candidate["id"] == "remote.socraticode" for candidate in result["candidates"])
    assert service.proxy_manager.remote_tool_calls == 0


@pytest.mark.asyncio
async def test_tool_card_resolver_uses_registered_schema():
    service = LocalReasoningToolService(
        proxy_manager=FakeProxy(),
        internal_mcp=FakeInternalMCP(),
        orchestrator=SimpleNamespace(event_store=None),
    )

    cards = await service.tool_card_resolver(["local.knowledge_search_context"])

    assert cards["tool_cards"][0]["target"] == "local.knowledge_search_context"
    assert cards["tool_cards"][0]["input_schema"]["properties"]["query"]["type"] == "string"
    assert "embedding_text" in cards["tool_cards"][0]


@pytest.mark.asyncio
async def test_tool_card_resolver_handles_remote_registry_without_starting_server():
    service = LocalReasoningToolService(
        proxy_manager=FakeProxy(),
        internal_mcp=FakeInternalMCP(),
        orchestrator=SimpleNamespace(event_store=None),
    )

    cards = await service.tool_card_resolver(["remote.socraticode"])

    assert cards["tool_cards"][0]["target"] == "remote.socraticode"
    assert cards["tool_cards"][0]["side_effect_level"] == "external"
    assert service.proxy_manager.remote_tool_calls == 0


@pytest.mark.asyncio
async def test_reasoned_rerank_tool_returns_json_serializable_payload():
    service = LocalReasoningToolService(
        proxy_manager=FakeProxy(),
        internal_mcp=FakeInternalMCP(),
        orchestrator=SimpleNamespace(event_store=None),
    )

    payload = await service.reasoned_rerank(
        goal="retrieve context",
        candidates=[
            {"id": "local.knowledge_search_context", "text": "search context", "score": 0.5}
        ],
        max_selected=1,
        mode="shadow",
    )

    json.dumps(payload)
    assert payload["ranked"][0]["id"] == "local.knowledge_search_context"
