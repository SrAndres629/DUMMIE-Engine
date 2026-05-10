import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator import CognitiveOrchestrator


class _Dummy:
    pass


@pytest.mark.asyncio
async def test_bridge_exposes_lamport_clock_and_ticks_on_intent():
    orchestrator = CognitiveOrchestrator(
        shield_port=_Dummy(),
        event_store=_Dummy(),
        ledger_audit=_Dummy(),
        session_ledger=_Dummy(),
        skill_repo=_Dummy(),
    )

    assert orchestrator.lamport_clock == 0

    class _Intent:
        goal = "bridge contract"

    await orchestrator.process_intent(_Intent())
    assert orchestrator.lamport_clock == 1


@pytest.mark.asyncio
async def test_bridge_handle_task_returns_legacy_ack():
    orchestrator = CognitiveOrchestrator(
        shield_port=_Dummy(),
        event_store=_Dummy(),
        ledger_audit=_Dummy(),
        session_ledger=_Dummy(),
        skill_repo=_Dummy(),
    )

    result = await orchestrator.handle_task("any task")
    assert result == "INTENT_QUEUED_L2_VALIDATED"
    assert orchestrator.lamport_clock == 1
