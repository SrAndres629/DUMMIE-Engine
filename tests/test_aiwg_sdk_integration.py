from __future__ import annotations

from dummie import DummieEngine


def test_sdk_acceptance_flow() -> None:
    engine = DummieEngine.load()
    status = engine.status()
    assert status.preflight.get("status") == "PASS"

    response = engine.advise("quiero que mi negocio facture 10000 USD mensuales")
    assert response.goal_type == "revenue"
    assert len(response.strategic_questions) > 0
    assert len(response.tool_opportunities) > 0
