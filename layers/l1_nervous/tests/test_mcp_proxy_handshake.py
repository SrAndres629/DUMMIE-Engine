import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest

from mcp_proxy import MCPConnectionState, MCPProxyManager


class FakeStdin:
    def __init__(self):
        self.messages = []

    def write(self, data):
        self.messages.append(json.loads(data.decode()))

    async def drain(self):
        return None


class FakeStdout:
    def __init__(self, responses):
        self.responses = [json.dumps(r).encode() + b"\n" for r in responses]

    async def readline(self):
        if not self.responses:
            return b""
        return self.responses.pop(0)


class FakeProcess:
    returncode = None

    def __init__(self, responses):
        self.stdin = FakeStdin()
        self.stdout = FakeStdout(responses)
        self.stderr = FakeStdout([])


@pytest.mark.asyncio
async def test_proxy_reaches_ready_before_tool_call(tmp_path):
    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"obsidian": {"command": "fake"}}}))
    manager = MCPProxyManager(str(cfg))
    process = FakeProcess(
        [
            {"jsonrpc": "2.0", "id": "init", "result": {"capabilities": {}, "serverInfo": {"name": "fake"}}},
            {"jsonrpc": "2.0", "id": "list", "result": {"tools": [{"name": "obsidian_get_file_contents"}]}},
            {"jsonrpc": "2.0", "id": "call", "result": {"content": [{"type": "text", "text": "ok"}]}},
        ]
    )

    async def fake_ensure_process(server_name):
        return process

    manager._ensure_process = fake_ensure_process

    response = await manager.call_tool("obsidian", "obsidian_get_file_contents", {"filepath": "A.md"})

    methods = [message["method"] for message in process.stdin.messages]
    assert methods == ["initialize", "notifications/initialized", "tools/list", "tools/call"]
    assert manager.server_states["obsidian"] == MCPConnectionState.READY
    assert response["result"]["content"][0]["text"] == "ok"


@pytest.mark.asyncio
async def test_get_tools_uses_discovery_cache_after_ready(tmp_path):
    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"obsidian": {"command": "fake"}}}))
    manager = MCPProxyManager(str(cfg))
    process = FakeProcess(
        [
            {"jsonrpc": "2.0", "id": "init", "result": {"capabilities": {}}},
            {"jsonrpc": "2.0", "id": "list", "result": {"tools": [{"name": "obsidian_simple_search"}]}},
        ]
    )

    async def fake_ensure_process(server_name):
        return process

    manager._ensure_process = fake_ensure_process

    tools = await manager.get_tools_for_server("obsidian")

    assert tools == [{"name": "obsidian_simple_search"}]
    assert [message["method"] for message in process.stdin.messages] == [
        "initialize",
        "notifications/initialized",
        "tools/list",
    ]
