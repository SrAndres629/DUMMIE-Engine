import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest
from mcp.server.fastmcp import FastMCP

from tools_impl.gateway import register_gateway_tools


class FakeProxy:
    def __init__(self):
        self.servers = {"filesystem": {}}
        self.calls = []

    async def call_tool(self, server_name, tool_name, arguments):
        self.calls.append((server_name, tool_name, arguments))
        return {"result": {"content": [{"type": "text", "text": "called"}]}}

    async def get_tools_for_server(self, server_name):
        return []


class FakeUseCases:
    def __init__(self):
        self.proxy_manager = FakeProxy()
        self.orchestrator = type("Orchestrator", (), {"lamport_clock": 1})()


@pytest.mark.asyncio
async def test_exec_remote_tool_blocks_mutation_before_proxy_call():
    mcp = FastMCP("test")
    use_cases = FakeUseCases()
    register_gateway_tools(mcp, use_cases)
    tool = mcp._tool_manager._tools["exec_remote_tool"].fn

    result = await tool("filesystem", "write_file", {"path": "A.md", "content": "x"})

    assert result == "SDD_BLOCKED: missing_sdd_admission"
    assert use_cases.proxy_manager.calls == []


@pytest.mark.asyncio
async def test_exec_remote_tool_auto_admits_when_active_spec_covers_path(tmp_path, monkeypatch):
    spec_dir = tmp_path / "doc" / "specs"
    spec_dir.mkdir(parents=True)
    (spec_dir / "22_sdd_executable_contracts.md").write_text(
        """---
status: "ACTIVE"
---
# SDD

## Physical Evidence
- `README.md`
"""
    )
    monkeypatch.setenv("DUMMIE_ROOT", str(tmp_path))
    mcp = FastMCP("test")
    use_cases = FakeUseCases()
    register_gateway_tools(mcp, use_cases)
    tool = mcp._tool_manager._tools["exec_remote_tool"].fn

    result = await tool("filesystem", "write_file", {"path": "README.md", "content": "x"})

    assert result == "called"
    assert use_cases.proxy_manager.calls == [
        ("filesystem", "write_file", {"path": "README.md", "content": "x"})
    ]
