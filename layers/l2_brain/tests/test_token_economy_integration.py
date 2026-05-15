import pytest
from layers.l2_brain.model_router import ModelRouter, ModelRegistry, ModelConfig, ModelTier
from layers.l2_brain.token_cost_ledger import TokenCostLedger
from layers.l2_brain.outcome_evaluator import OutcomeEvaluator
from layers.l2_brain.daemon_outcome import DaemonOutcome
from layers.l2_brain.gateway_contract import SagaTransaction

class MockDaemon:
    def __init__(self, ledger, budget_manager):
        self.token_ledger = ledger
        self.budget_manager = budget_manager
        self.mission_id = "m1"
        self.session_id = "s1"
        self.last_context_packet = {"items": [{"id": "c1", "estimated_tokens": 5000, "priority": "high"}]}
        self.last_allocated_budget = {"total_budget": 4096}

def test_integration_model_router_records_to_ledger(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    registry = ModelRegistry()
    registry.models[ModelTier.LOCAL_FAST] = [
        ModelConfig(model_id="m1", tier=ModelTier.LOCAL_FAST, provider="ollama")
    ]
    router = ModelRouter(registry=registry, ledger=ledger)
    
    # Route should trigger record_usage
    router.route("test prompt", mission_id="m1")
    
    summary = ledger.summarize_mission("m1")
    assert summary["event_count"] == 1
    assert summary["total_input_tokens"] > 0
    assert summary["total_raw_tokens_seen"] > 0

def test_integration_outcome_evaluator_includes_token_economy(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    ledger.record_usage({"mission_id": "m1", "input_tokens": 100, "output_tokens": 50})
    
    from layers.l2_brain.context_budget_manager import ContextBudgetManager
    budget_manager = ContextBudgetManager()
    
    daemon = MockDaemon(ledger, budget_manager)
    evaluator = OutcomeEvaluator(daemon=daemon)
    
    saga = SagaTransaction(transaction_id="t1", context_token="ct1", steps=[])
    outcome = evaluator.build_outcome(status="SUCCESS", transaction_id="t1", saga=saga, mission_id="m1")
    
    efficiency = outcome["efficiency"]
    assert "token_economy_summary" in efficiency
    assert efficiency["token_economy_summary"]["billable_tokens_estimate"] == 150
    assert efficiency["budget_pressure"] == "extreme" # 5000/4096 > 1.0

def test_integration_model_router_explicit_usage(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    router = ModelRouter(ledger=ledger)
    
    router.emit_usage_event(
        input_tokens=100,
        output_tokens=50,
        tier=ModelTier.CLOUD_STD,
        provider="openai",
        mission_id="m2"
    )
    
    summary = ledger.summarize_mission("m2")
    assert summary["total_input_tokens"] == 100
    assert summary["total_output_tokens"] == 50
    
    events = list(ledger.iter_usage(mission_id="m2"))
    assert events[0]["estimated"] is False
    assert events[0]["model_tier"] == "cloud_std"
