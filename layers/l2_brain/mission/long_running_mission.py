from __future__ import annotations

from typing import Any

from layers.l2_brain.phase_ledger import PhaseLedger


class LongRunningMissionRuntime:
    def __init__(self, ledger: PhaseLedger | None = None):
        self.ledger = ledger or PhaseLedger()

    def start_mission(self, mission_id: str, user_goal: str, phases: list[dict]) -> dict:
        return self.ledger.create_mission(mission_id, user_goal, phases)

    def start_phase(self, mission_id: str, phase_id: str) -> dict:
        state = self.ledger.current_state(mission_id)
        phase = state["phases"].get(phase_id)
        if not phase:
            event = self.ledger.append_event(
                mission_id,
                {
                    "event_type": "PHASE_BLOCKED",
                    "phase_id": phase_id,
                    "reason": "phase_not_registered",
                },
            )
            self._refresh_files(mission_id)
            return event

        pending = [dep for dep in phase.get("depends_on", []) if dep not in state["completed_phases"]]
        if pending:
            event = self.ledger.append_event(
                mission_id,
                {
                    "event_type": "PHASE_BLOCKED",
                    "phase_id": phase_id,
                    "reason": f"pending_dependencies:{','.join(pending)}",
                },
            )
            self._refresh_files(mission_id)
            return event

        event = self.ledger.append_event(
            mission_id,
            {
                "event_type": "PHASE_STARTED",
                "phase_id": phase_id,
            },
        )
        self._refresh_files(mission_id)
        return event

    def complete_phase(self, mission_id: str, phase_id: str, outcome: dict) -> dict:
        checkpoint = self.ledger.create_checkpoint(mission_id, phase_id, _checkpoint_payload(outcome))
        event = self.ledger.append_event(
            mission_id,
            {
                "event_type": "PHASE_COMPLETED",
                "phase_id": phase_id,
                "outcome": {
                    **outcome,
                    "checkpoint_ref": checkpoint.get("checkpoint_ref", ""),
                },
            },
        )
        self._refresh_files(mission_id)
        return event

    def block_phase(self, mission_id: str, phase_id: str, reason: str) -> dict:
        event = self.ledger.append_event(
            mission_id,
            {
                "event_type": "PHASE_BLOCKED",
                "phase_id": phase_id,
                "reason": reason,
            },
        )
        self._refresh_files(mission_id)
        return event

    def pause_mission(self, mission_id: str, reason: str) -> dict:
        event = self.ledger.append_event(
            mission_id,
            {
                "event_type": "PHASE_PAUSED",
                "reason": reason,
            },
        )
        self._refresh_files(mission_id)
        return event

    def resume_mission(self, mission_id: str) -> dict:
        event = self.ledger.append_event(
            mission_id,
            {
                "event_type": "PHASE_RESUMED",
            },
        )
        self._refresh_files(mission_id)
        return event

    def current_state(self, mission_id: str) -> dict:
        return self.ledger.current_state(mission_id)

    def recovery_packet(self, mission_id: str) -> dict:
        return self.ledger.generate_recovery_packet(mission_id)

    def _refresh_files(self, mission_id: str) -> None:
        self.ledger.select_next_action(mission_id)


def _checkpoint_payload(outcome: dict[str, Any]) -> dict:
    return {
        "outcome": outcome,
        "evidence_refs": list(outcome.get("evidence_refs", []) or []),
        "tests": dict(outcome.get("tests", {}) or {}),
        "key_decisions": list(outcome.get("key_decisions", []) or []),
    }
