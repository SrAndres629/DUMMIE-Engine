from dummie.engine import DummieEngine

def test_engine_load():
    engine = DummieEngine.load()
    assert engine is not None

def test_engine_status():
    engine = DummieEngine.load()
    status = engine.status()
    assert status.decision == "PASS"
    assert status.preflight.get("status") == "PASS"

def test_engine_advise():
    engine = DummieEngine.load()
    res = engine.advise("quiero facturar 10000 USD mensuales")
    assert res.goal_type == "revenue"
    assert len(res.strategic_questions) > 0
    assert len(res.tool_opportunities) > 0
