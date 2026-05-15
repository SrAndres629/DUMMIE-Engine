from unittest.mock import MagicMock

import pytest

from layers.l2_brain.daemon import DummieDaemon
from layers.l2_brain.event_bus import AsyncEventBus
from layers.l2_brain.gateway_contract import SagaTransaction
from layers.l2_brain.long_running_mission import LongRunningMissionRuntime
from layers.l2_brain.phase_ledger import PhaseLedger


def _runtime(tmp_path):
    return LongRunningMissionRuntime(PhaseLedger(root=tmp_path))


def test_long_running_runtime_full_lifecycle_uses_phase_ledger(tmp_path):
    runtime = _runtime(tmp_path)

    created = runtime.start_mission(
        "mission_a",
        "Do durable multi-phase work",
        [
            {"phase_id": "phase_1", "authority_level": "A0_OBSERVER"},
            {"phase_id": "phase_2", "authority_level": "A1_WORKSPACE_OP", "depends_on": ["phase_1"]},
        ],
    )
    blocked = runtime.start_phase("mission_a", "phase_2")
    started = runtime.start_phase("mission_a", "phase_1")
    completed = runtime.complete_phase(
        "mission_a",
        "phase_1",
        {"status": "SUCCESS", "evidence_refs": ["pytest://long_running"], "tests": {"commands": ["pytest"], "passed": 1}},
    )
    paused = runtime.pause_mission("mission_a", "operator checkpoint")
    resumed = runtime.resume_mission("mission_a")
    next_phase = runtime.start_phase("mission_a", "phase_2")
    state = runtime.current_state("mission_a")

    assert created["status"] == "created"
    assert blocked["event_type"] == "PHASE_BLOCKED"
    assert "pending_dependencies" in blocked["reason"]
    assert started["event_type"] == "PHASE_STARTED"
    assert completed["event_type"] == "PHASE_COMPLETED"
    assert paused["event_type"] == "PHASE_PAUSED"
    assert resumed["event_type"] == "PHASE_RESUMED"
    assert next_phase["event_type"] == "PHASE_STARTED"
    assert state["phases"]["phase_1"]["status"] == "completed"
    assert state["phases"]["phase_2"]["status"] == "running"


def test_long_running_runtime_blocks_phase_and_generates_recovery_packet(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.start_mission("mission_b", "Recover from blocked work", [{"phase_id": "phase_1"}])

    blocked = runtime.block_phase("mission_b", "phase_1", "missing evidence")
    recovery = runtime.recovery_packet("mission_b")
    next_action = runtime.ledger.select_next_action("mission_b")

    assert blocked["event_type"] == "PHASE_BLOCKED"
    assert recovery["recovery_packet_ref"].endswith("recovery_packet.md")
    assert next_action["recommended"] == "inspect_blocked_phase"
    assert (tmp_path / "mission_b" / "recovery_packet.md").exists()
    packet = (tmp_path / "mission_b" / "recovery_packet.md").read_text(encoding="utf-8")
    assert "## Do Not Repeat" in packet
    assert "chain-of-thought" not in packet.lower()


def test_complete_phase_does_not_mark_completed_if_checkpoint_fails(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.start_mission("mission_c", "Avoid false completion", [{"phase_id": "phase_1"}])
    runtime.start_phase("mission_c", "phase_1")
    runtime.ledger.create_checkpoint = MagicMock(side_effect=OSError("disk full"))

    with pytest.raises(OSError, match="disk full"):
        runtime.complete_phase("mission_c", "phase_1", {"status": "SUCCESS"})

    state = runtime.current_state("mission_c")
    assert state["phases"]["phase_1"]["status"] == "running"


def test_long_running_runtime_rejects_private_reasoning(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.start_mission("mission_d", "Protect public recovery data", [{"phase_id": "phase_1"}])
    runtime.start_phase("mission_d", "phase_1")

    with pytest.raises(ValueError, match="private"):
        runtime.complete_phase("mission_d", "phase_1", {"notes": "private reasoning must not persist"})


def test_daemon_outcome_includes_mission_state_when_runtime_exists(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.start_mission("mission_e", "Expose mission state in outcome", [{"phase_id": "phase_1"}])
    runtime.start_phase("mission_e", "phase_1")

    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=MagicMock(),
        event_bus=MagicMock(spec=AsyncEventBus),
    )
    daemon.mission_runtime = runtime
    saga = SagaTransaction(transaction_id="tx-mission", context_token="ctx", steps=[])

    outcome = daemon._build_outcome(
        status="PARTIAL",
        transaction_id="tx-mission",
        saga=saga,
        mission_id="mission_e",
        phase_id="phase_1",
    )

    assert outcome["current_mission_state"]["mission_id"] == "mission_e"
    assert outcome["current_mission_state"]["current_phase"] == "phase_1"
    assert outcome["next_action"]["recommended"]


def test_daemon_outcome_fallback_without_mission_runtime(tmp_path):
    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=MagicMock(),
        event_bus=MagicMock(spec=AsyncEventBus),
    )
    daemon.mission_runtime = None
    saga = SagaTransaction(transaction_id="tx-no-runtime", context_token="ctx", steps=[])

    outcome = daemon._build_outcome(
        status="SUCCESS",
        transaction_id="tx-no-runtime",
        saga=saga,
        mission_id="mission_missing_runtime",
        phase_id="phase_1",
    )

    assert outcome["mission_id"] == "mission_missing_runtime"
    assert "current_mission_state" not in outcome
