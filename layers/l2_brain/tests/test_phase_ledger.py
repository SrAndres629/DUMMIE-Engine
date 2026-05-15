import json

import pytest

from layers.l2_brain.phase_ledger import PhaseLedger


def test_phase_ledger_creates_mission_registers_phases_and_reconstructs_state(tmp_path):
    ledger = PhaseLedger(root=tmp_path)

    state = ledger.create_mission(
        mission_id="mission_1",
        user_goal="Build resumable missions",
        phases=[
            {"phase_id": "phase_1", "authority_level": "A0_OBSERVER"},
            {"phase_id": "phase_2", "authority_level": "A1_WORKSPACE_OP", "depends_on": ["phase_1"]},
        ],
    )

    ledger_path = tmp_path / "mission_1" / "phase_ledger.jsonl"
    assert ledger_path.exists()
    assert state["mission_id"] == "mission_1"
    assert state["status"] == "created"
    assert state["phases"]["phase_1"]["status"] == "registered"
    assert state["phases"]["phase_2"]["depends_on"] == ["phase_1"]

    event_types = [event["event_type"] for event in ledger.iter_events("mission_1")]
    assert event_types == ["MISSION_CREATED", "PHASE_REGISTERED", "PHASE_REGISTERED"]

    reconstructed = ledger.current_state("mission_1")
    assert reconstructed["user_goal"] == "Build resumable missions"
    assert reconstructed["phases"]["phase_1"]["authority_level"] == "A0_OBSERVER"


def test_phase_ledger_lifecycle_checkpoint_recovery_and_next_action(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission(
        "mission_2",
        "Keep a mission alive across sessions",
        [
            {"phase_id": "phase_1", "authority_level": "A0_OBSERVER"},
            {"phase_id": "phase_2", "authority_level": "A1_WORKSPACE_OP", "depends_on": ["phase_1"]},
        ],
    )

    ledger.append_event("mission_2", {"event_type": "PHASE_STARTED", "phase_id": "phase_1"})
    checkpoint = ledger.create_checkpoint(
        "mission_2",
        "phase_1",
        {
            "evidence_refs": ["pytest://phase_ledger"],
            "tests": {"commands": ["pytest test_phase_ledger.py"], "passed": 1, "failed": 0},
            "key_decisions": ["Use append-only JSONL"],
        },
    )
    ledger.append_event(
        "mission_2",
        {
            "event_type": "PHASE_COMPLETED",
            "phase_id": "phase_1",
            "outcome": {"status": "SUCCESS", "checkpoint_ref": checkpoint["checkpoint_ref"]},
        },
    )

    next_action = ledger.select_next_action("mission_2")
    recovery = ledger.generate_recovery_packet("mission_2")
    state = ledger.current_state("mission_2")

    assert next_action["recommended"] == "start_phase"
    assert next_action["phase_id"] == "phase_2"
    assert recovery["recovery_packet_ref"].endswith("recovery_packet.md")
    assert (tmp_path / "mission_2" / "current_state.json").exists()
    assert (tmp_path / "mission_2" / "next_action.json").exists()
    assert (tmp_path / "mission_2" / "recovery_packet.md").exists()
    assert state["completed_phases"] == ["phase_1"]
    assert state["tests_last_run"]["commands"] == ["pytest test_phase_ledger.py"]


def test_phase_ledger_next_action_continues_running_phase(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission(
        "mission_running",
        "Keep working",
        [
            {"phase_id": "phase_1", "authority_level": "A0_OBSERVER"},
            {"phase_id": "phase_2", "authority_level": "A1_WORKSPACE_OP", "depends_on": ["phase_1"]},
        ],
    )
    ledger.append_event("mission_running", {"event_type": "PHASE_STARTED", "phase_id": "phase_1"})

    next_action = ledger.select_next_action("mission_running")

    assert next_action["recommended"] == "continue_phase"
    assert next_action["phase_id"] == "phase_1"


def test_phase_ledger_blocks_path_traversal_and_private_reasoning(tmp_path):
    ledger = PhaseLedger(root=tmp_path)

    with pytest.raises(ValueError, match="path traversal"):
        ledger.create_mission("../secret", "bad", [])

    ledger.create_mission("mission_3", "Protect mission files", [{"phase_id": "phase_1"}])

    with pytest.raises(ValueError, match="private"):
        ledger.create_checkpoint("mission_3", "phase_1", {"notes": "chain_of_thought://private"})

    with pytest.raises(ValueError, match="secret"):
        ledger.append_event("mission_3", {"event_type": "PHASE_BLOCKED", "phase_id": "phase_1", "reason": "read .env"})


def test_phase_ledger_rejects_noncanonical_authority_level(tmp_path):
    ledger = PhaseLedger(root=tmp_path)

    with pytest.raises(ValueError, match="authority_level"):
        ledger.create_mission("mission_bad_auth", "Bad authority", [{"phase_id": "phase_1", "authority_level": "A1_OPERATOR"}])


def test_phase_ledger_jsonl_is_append_only(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_4", "Append only", [{"phase_id": "phase_1"}])
    ledger.append_event("mission_4", {"event_type": "PHASE_STARTED", "phase_id": "phase_1"})
    ledger.append_event("mission_4", {"event_type": "PHASE_PAUSED", "reason": "operator break"})

    ledger_path = tmp_path / "mission_4" / "phase_ledger.jsonl"
    lines = ledger_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 4
    assert [json.loads(line)["event_type"] for line in lines][-2:] == ["PHASE_STARTED", "PHASE_PAUSED"]
