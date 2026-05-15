import json

import pytest

from layers.l2_brain.mission_runtime_contract import MissionRuntimeContract


def test_mission_runtime_contract_serializes_json():
    contract = MissionRuntimeContract(
        mission_id="mission-1",
        phase_id="phase-1",
        status="running",
        recovery_packet_ref=".aiwg/reports/recovery.json",
        next_action_ref=".aiwg/reports/next.json",
    )

    payload = json.loads(contract.to_json())

    assert payload["mission_id"] == "mission-1"
    assert payload["phase_id"] == "phase-1"
    assert payload["status"] == "running"
    assert payload["resume_token"]


def test_mission_runtime_contract_rejects_path_traversal_in_mission_id():
    with pytest.raises(ValueError, match="path traversal"):
        MissionRuntimeContract(mission_id="../secrets", phase_id="phase-1")


def test_mission_runtime_contract_accepts_valid_phase_id():
    contract = MissionRuntimeContract(mission_id="mission_1", phase_id="phase-2")

    assert contract.phase_id == "phase-2"


def test_mission_runtime_contract_generates_deterministic_resume_token():
    left = MissionRuntimeContract(mission_id="mission-1", phase_id="phase-1", status="paused")
    right = MissionRuntimeContract(mission_id="mission-1", phase_id="phase-1", status="paused")

    assert left.resume_token == right.resume_token


def test_mission_runtime_contract_does_not_contain_private_chain_of_thought():
    contract = MissionRuntimeContract(
        mission_id="mission-1",
        phase_id="phase-1",
        private_reasoning_refs=["chain_of_thought://private"],
    )

    payload = contract.to_json().lower()

    assert "chain_of_thought" not in payload
    assert "private reasoning" not in payload
