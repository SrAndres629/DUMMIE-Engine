import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
L3 = ROOT.parents[0] / "l3_shield"
for path in (ROOT, L2, L3):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest

from tools_impl.knowledge import KnowledgeToolService


class FakeProxy:
    def __init__(self):
        self.calls = []

    async def call_tool(self, server_name, tool_name, arguments):
        self.calls.append((server_name, tool_name, arguments))
        return {"result": {"content": [{"type": "text", "text": "ok"}]}}


@pytest.mark.asyncio
async def test_wisdom_export_uses_append_only_policy():
    proxy = FakeProxy()
    service = KnowledgeToolService(proxy)

    result = await service.export_decision_summary(
        decision_id="dec-1",
        summary="Use ports",
        rationale="Keep L2 sovereign",
        target_file="DUMMIE/Decisions.md",
    )

    assert result["policy"] == "L3_AUTO_APPEND"
    assert proxy.calls[0][1] == "obsidian_append_content"


@pytest.mark.asyncio
async def test_generic_delete_is_not_exposed():
    service = KnowledgeToolService(FakeProxy())

    assert not hasattr(service, "delete_file")
