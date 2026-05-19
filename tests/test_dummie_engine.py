from __future__ import annotations

from dummie.engine import DummieEngine


def test_engine_load() -> None:
    engine = DummieEngine.load()
    assert engine is not None


def test_engine_status_runs() -> None:
    engine = DummieEngine.load()
    status = engine.status()
    assert status.decision in {"PASS", "FAIL"}
    assert status.preflight.get("status") == "PASS"
    assert isinstance(status.providers, dict)


def test_engine_advise_business_revenue_goal() -> None:
    engine = DummieEngine.load()
    res = engine.advise("quiero facturar 10000 USD mensuales")
    assert res.goal_type == "revenue"
    assert len(res.strategic_questions) >= 5
    assert len(res.tool_opportunities) >= 3
    assert res.receipt.get("status") == "PASS"
