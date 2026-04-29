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


def _make_daemon():
    daemon = DummieDaemon(
        ledger_path="/tmp/ledger.jsonl",
        mcp_gateway=object(),
        event_bus=_NoopEventBus(),
        skill_binder=None,
    )
    daemon.s_shield = _AllowAllAuditor()
    daemon.e_shield = _AllowAllAuditor()
    daemon.l_shield = _AllowAllAuditor()
    daemon.muscle = _CaptureExecutor()
    return daemon


@pytest.mark.asyncio
async def test_runtime_guards_block_daemon_before_tool_execution():
    daemon = _make_daemon()
    request = GatewayRequest(
        session_id="S-G1",
        goal="Blocked by runtime guard",
        dag_xml=(
            "<dag provider_ready='false' parent_spec_approved='false'>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "FAILED"
    assert outcome["gate_status"] == "BLOCK"
    assert "provider_not_ready" in outcome["gate_reasons"]
    assert "parent_spec_not_approved" in outcome["gate_reasons"]
    assert daemon.muscle.calls == []


@pytest.mark.asyncio
async def test_high_entropy_bundle_requires_review_before_tool_execution():
    daemon = _make_daemon()
    request = GatewayRequest(
        session_id="S-G2",
        goal="Blocked by uncertainty",
        dag_xml=(
            "<dag>"
            "<hypothesis_bundle entropy_threshold='0.5'>"
            "<hypothesis id='h1' weight='1.0'>Path A</hypothesis>"
            "<hypothesis id='h2' weight='1.0'>Path B</hypothesis>"
            "</hypothesis_bundle>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "FAILED"
    assert outcome["gate_status"] == "REVIEW"
    assert "high_entropy_requires_review" in outcome["gate_reasons"]
    assert daemon.muscle.calls == []


@pytest.mark.asyncio
async def test_counterfactual_threshold_blocks_low_utility_action():
    daemon = _make_daemon()
    request = GatewayRequest(
        session_id="S-G3",
        goal="Block low-value destructive action",
        dag_xml=(
            "<dag min_counterfactual_score='0.5'>"
            "<task id='t1' server='filesystem' tool='delete' utility='0.1' cost='2.0'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "FAILED"
    assert outcome["gate_status"] == "BLOCK"
    assert "counterfactual_score_below_threshold" in outcome["gate_reasons"]
    assert daemon.muscle.calls == []
