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


class _CapturePlanner:
    def __init__(self, plan: dict):
        self.plan = plan
        self.calls = []

    def propose_reflective_plan(self, goal: str, preferred_master_skill: str = ""):
        self.calls.append((goal, preferred_master_skill))
        return self.plan


class _NoopEventBus:
    async def wait_for_request(self):
        raise NotImplementedError


def _make_daemon(planner=None):
    daemon = DummieDaemon(
        ledger_path="/tmp/ledger.jsonl",
        mcp_gateway=object(),
        event_bus=_NoopEventBus(),
        skill_binder=planner,
    )
    daemon.s_shield = _AllowAllAuditor()
    daemon.e_shield = _AllowAllAuditor()
    daemon.l_shield = _AllowAllAuditor()
    daemon.muscle = _CaptureExecutor()
    return daemon


def _two_task_request() -> GatewayRequest:
    return GatewayRequest(
        session_id="S-01",
        goal="Analizar workspace y actualizar archivos de configuración",
        dag_xml=(
            "<dag>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "<task id='t2' server='filesystem' tool='write'>"
            "<arguments>{\"path\": \"README.md\", \"content\": \"ok\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )


@pytest.mark.asyncio
async def test_all_tasks_pass_through_hierarchical_planner_before_tool_execution():
    planner = _CapturePlanner(
        {
            "goal": "g",
            "plan_type": "hierarchical",
            "master_skill": "sw.master.operations",
            "steps": [
                {"order": 1, "skill_id": "sw.subskill.read", "name": "read"},
                {"order": 2, "skill_id": "sw.subskill.write", "name": "write"},
            ],
        }
    )
    daemon = _make_daemon(planner)
    request = _two_task_request()

    outcome = await daemon.process_request(request)

    assert planner.calls == [(request.goal, "")]
    assert outcome["status"] == "SUCCESS"
    assert daemon.last_plan["master_skill"] == "sw.master.operations"
    assert daemon.last_task_routes[0]["subskill_id"] == "sw.subskill.read"
    assert daemon.last_task_routes[1]["subskill_id"] == "sw.subskill.write"
    assert len(daemon.muscle.calls) == 2


@pytest.mark.asyncio
async def test_invalid_hierarchical_plan_blocks_tool_execution():
    planner = _CapturePlanner({"plan_type": "hierarchical", "master_skill": "", "steps": []})
    daemon = _make_daemon(planner)

    outcome = await daemon.process_request(_two_task_request())

    assert outcome["status"] == "FAILED"
    assert "invalid plan" in outcome["error"]
    assert daemon.muscle.calls == []


@pytest.mark.asyncio
async def test_daemon_uses_hierarchical_fallback_when_planner_not_injected():
    daemon = _make_daemon(planner=None)
    request = _two_task_request()

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "SUCCESS"
    assert daemon.last_plan["plan_type"] == "hierarchical_fallback"
    assert daemon.last_plan["master_skill"] == "sw.master.default"
    assert daemon.last_task_routes[0]["subskill_id"] == "sw.subskill.dispatch"
    assert len(daemon.muscle.calls) == 2


@pytest.mark.asyncio
async def test_task_can_pin_subskill_id_in_dag_node():
    planner = _CapturePlanner(
        {
            "goal": "g",
            "plan_type": "hierarchical",
            "master_skill": "sw.master.operations",
            "steps": [
                {"order": 1, "skill_id": "sw.subskill.read", "name": "read"},
                {"order": 2, "skill_id": "sw.subskill.write", "name": "write"},
            ],
        }
    )
    daemon = _make_daemon(planner)
    request = GatewayRequest(
        session_id="S-02",
        goal="Enforce explicit subskill",
        dag_xml=(
            "<dag>"
            "<task id='t1' server='filesystem' tool='read' subskill='sw.subskill.write'>"
            "<arguments>{\"path\": \"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "SUCCESS"
    assert daemon.last_task_routes[0]["subskill_id"] == "sw.subskill.write"
