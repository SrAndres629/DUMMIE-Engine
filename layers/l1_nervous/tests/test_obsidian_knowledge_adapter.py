import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest

from knowledge_adapters import ObsidianKnowledgeAdapter


class FakeProxy:
    def __init__(self):
        self.calls = []

    async def call_tool(self, server_name, tool_name, arguments):
        self.calls.append((server_name, tool_name, arguments))
        if tool_name == "obsidian_simple_search":
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": '[{"filename":"A.md","score":0.9,"matches":[{"context":"hello"}]}]',
                        }
                    ]
                }
            }
        return {"result": {"content": [{"type": "text", "text": "# A\nhello"}]}}


@pytest.mark.asyncio
async def test_search_context_uses_obsidian_simple_search():
    proxy = FakeProxy()
    adapter = ObsidianKnowledgeAdapter(proxy)

    results = await adapter.search_context("hello", limit=5)

    assert proxy.calls[0] == (
        "obsidian",
        "obsidian_simple_search",
        {"query": "hello", "context_length": 200},
    )
    assert results[0].provider == "obsidian"
    assert results[0].source_uri == "obsidian://A.md"


@pytest.mark.asyncio
async def test_get_artifact_converts_file_to_source_artifact():
    proxy = FakeProxy()
    adapter = ObsidianKnowledgeAdapter(proxy)

    artifact = await adapter.get_artifact("obsidian://A.md")

    assert proxy.calls[0] == (
        "obsidian",
        "obsidian_get_file_contents",
        {"filepath": "A.md"},
    )
    assert artifact.content == "# A\nhello"
    assert artifact.payload_hash
