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

from mcp_transport import MCPTransport


class FakeProcess:
    def __init__(self):
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.returncode = None


@pytest.mark.asyncio
async def test_spawn_process_merges_config_env(monkeypatch):
    transport = MCPTransport()
    captured = {}

    async def fake_create_subprocess_exec(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setattr("mcp_transport._resolve_binary", lambda cmd: "/usr/bin/npx")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    await transport.spawn_process(
        "n8n",
        {
            "command": "npx",
            "args": ["-y", "n8n-mcp"],
            "env": {
                "MCP_MODE": "stdio",
                "N8N_API_URL": "http://127.0.0.1:5678",
            },
        },
    )

    assert captured["args"] == ("/usr/bin/npx", "-y", "n8n-mcp")
    assert captured["kwargs"]["env"]["MCP_MODE"] == "stdio"
    assert captured["kwargs"]["env"]["N8N_API_URL"] == "http://127.0.0.1:5678"
    assert captured["kwargs"]["env"]["PATH"] == os.environ["PATH"]
