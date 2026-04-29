import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daemon import DummieDaemon
from gateway_contract import GatewayRequest


class _AllowAllAuditor:
    async def audit(self, dag_xml: str, goal: str = ""):
        return True, "OK"


class _CaptureExecutor:
    def __init__(self):
        self.calls = []

    async def execute(self, server_name: str, tool_name: str, arguments: dict):
        self.calls.append((server_name, tool_name, arguments))
        return {"ok": True}


class _NoopEventBus:
    async def wait_for_request(self):
        raise NotImplementedError


class _MetaGateway:
    def __init__(self):
        self.calls = []

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        self.calls.append((server_name, tool_name, arguments))
        target = arguments["target"]
        if target == "local.semantic_recall":
            return json.dumps(
                {
                    "provider_status": "ok",
                    "candidates": [
                        {"id": "local.knowledge_search_context", "text": "search context", "score": 0.8}
                    ],
                }
            )
        if target == "local.reasoned_rerank":
            return json.dumps(
                {
                    "provider_status": "deterministic",
                    "ranked": [
                        {"id": "local.knowledge_search_context", "score": 0.9, "why": "grounded"}
                    ],
                }
            )
        if target == "local.context_shaper":
            return json.dumps(
                {
                    "task_brief": "Use grounded context",
                    "selected_tools": ["local.knowledge_search_context"],
                    "evidence_bundle": [],
                    "open_unknowns": [],
                    "execution_hint": "Use selected tools before cloud execution",
                    "estimated_tokens": 20,
                }
            )
        return "{}"


def _make_daemon(gateway):
    daemon = DummieDaemon(
        ledger_path="/tmp/ledger.jsonl",
        mcp_gateway=gateway,
        event_bus=_NoopEventBus(),
        skill_binder=None,
    )
    daemon.s_shield = _AllowAllAuditor()
    daemon.e_shield = _AllowAllAuditor()
    daemon.l_shield = _AllowAllAuditor()
    daemon.muscle = _CaptureExecutor()
    return daemon


@pytest.mark.asyncio
async def test_cognitive_preflight_runs_before_planning_when_enabled():
    gateway = _MetaGateway()
    daemon = _make_daemon(gateway)
    request = GatewayRequest(
        session_id="S-LR1",
        goal="Prepare context before executing task",
        dag_xml=(
            "<dag cognitive_preflight='true'>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "SUCCESS"
    assert outcome["cognitive_preflight"]["status"] == "READY"
    assert outcome["cognitive_preflight"]["selected_tools"] == ["local.knowledge_search_context"]
    assert [call[2]["target"] for call in gateway.calls] == [
        "local.semantic_recall",
        "local.reasoned_rerank",
        "local.context_shaper",
    ]


@pytest.mark.asyncio
async def test_cognitive_preflight_degrades_without_blocking_execution():
    class BrokenGateway:
        async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
            raise RuntimeError("gateway down")

    daemon = _make_daemon(BrokenGateway())
    request = GatewayRequest(
        session_id="S-LR2",
        goal="Continue if preflight is unavailable",
        dag_xml=(
            "<dag cognitive_preflight='true'>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "SUCCESS"
    assert outcome["cognitive_preflight"]["status"] == "DEGRADED"
    assert daemon.muscle.calls == [("filesystem", "read", {"path": "README.md"})]
