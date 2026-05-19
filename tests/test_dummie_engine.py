from __future__ import annotations

from pathlib import Path

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


def test_engine_chat_uses_runtime_pipeline_and_writes_traceability_assets() -> None:
    engine = DummieEngine.load()
    res = engine.chat("quiero lanzar una oferta para aumentar MRR en 90 dias", low_cost=True)
    assert res.decision == "PASS"
    assert res.preprocessing_provider in {"deterministic", "ollama"}
    assert res.routing_tier in {"local_fast", "local_deep", "cloud_std", "cloud_prem"}
    assert res.routing_model_id
    assert isinstance(res.strategic_questions, list)
    assert isinstance(res.tool_opportunities, list)
    assert isinstance(res.roadmap, list)
    assert Path(".aiwg/runtime/runtime_chat_registry.yaml").exists()
    assert Path(".aiwg/reports/runtime_chat_latest.json").exists()
    assert Path(".aiwg/reports/runtime_chat_trace_latest.json").exists()
