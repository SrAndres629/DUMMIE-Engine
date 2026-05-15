import pytest
from unittest.mock import AsyncMock, MagicMock
from layers.l2_brain.semantic_retrieval_runtime import SemanticRetrievalRuntime
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter

@pytest.mark.asyncio
async def test_srr_retrieve_for_prompt():
    adapter_mock = AsyncMock(spec=SocraticodeGatewayAdapter)
    adapter_mock.semantic_search.return_value = {
        "status": "READY",
        "results": [{"vault_id": "v1", "score": 0.9, "summary": "test"}],
        "fallback_used": False
    }
    
    runtime = SemanticRetrievalRuntime(socraticode_adapter=adapter_mock)
    res = await runtime.retrieve_for_prompt("hello")
    
    assert res["status"] == "READY"
    assert res["query"] == "hello"
    assert "v1" in res["vault_refs"]
    assert "vault:v1" in res["context_refs"]
    assert res["budget_pressure"] == "NORMAL"

@pytest.mark.asyncio
async def test_srr_budget_truncation():
    adapter_mock = AsyncMock()
    adapter_mock.semantic_search.return_value = {
        "status": "READY",
        "results": [
            {"vault_id": "v1"}, {"vault_id": "v2"}, {"vault_id": "v3"}
        ]
    }
    
    budget_mock = MagicMock()
    budget_mock.check_budget.return_value = {"ratio": 0.9} # High pressure
    
    runtime = SemanticRetrievalRuntime(adapter_mock, context_budget_manager=budget_mock)
    res = await runtime.retrieve_for_prompt("hello")
    
    assert res["budget_pressure"] == "HIGH"
    assert len(res["vault_refs"]) == 2 # Truncated
