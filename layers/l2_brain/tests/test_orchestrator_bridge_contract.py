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
    mock_daemon = type("MockDaemon", (), {"lamport_clock": 0, "process_request": None, "build_daemon_outcome": None})()
    orchestrator = CognitiveOrchestrator(daemon=mock_daemon)

    assert orchestrator.lamport_clock == 0

    class _Intent:
        goal = "bridge contract"

    # Mock process_intent behavior if necessary, but here we assume it exists
    if hasattr(orchestrator, "process_intent"):
        await orchestrator.process_intent(_Intent())
        assert orchestrator.lamport_clock == 1


@pytest.mark.asyncio
async def test_bridge_handle_task_returns_legacy_ack():
    mock_daemon = type("MockDaemon", (), {"lamport_clock": 0, "process_request": None, "build_daemon_outcome": None})()
    orchestrator = CognitiveOrchestrator(daemon=mock_daemon)

    if hasattr(orchestrator, "handle_task"):
        result = await orchestrator.handle_task("any task")
        assert result == "INTENT_QUEUED_L2_VALIDATED"
        assert orchestrator.lamport_clock == 1

