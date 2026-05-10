import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class _FakeMCP:
    def __init__(self):
        self._tools = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn

        return decorator


def _register_core_tools(root_dir: str):
    l1_root = Path(__file__).resolve().parents[1]
    tools_impl = l1_root / "tools_impl"
    for candidate in (l1_root, tools_impl):
        path = str(candidate)
        if path not in sys.path:
            sys.path.insert(0, path)

    use_cases = MagicMock()
    use_cases.orchestrator = MagicMock()

    from tools_impl.core import register_core_tools

    mcp = _FakeMCP()
    register_core_tools(mcp, use_cases, root_dir)
    return mcp._tools


def test_operational_truth_tool_is_registered(tmp_path):
    tools = _register_core_tools(str(tmp_path))

    assert "operational_truth_report" in tools


@pytest.mark.asyncio
async def test_operational_truth_tool_returns_json(tmp_path):
    tools = _register_core_tools(str(tmp_path))

    payload = json.loads(await tools["operational_truth_report"](format="json"))

    assert "summary" in payload
    assert "checks" in payload
