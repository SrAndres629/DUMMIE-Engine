import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from layers.l2_brain.semantic_retrieval_runtime import SemanticRetrievalRuntime
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter
from layers.l2_brain.vault_context_resolver import VaultContextResolver

@pytest.mark.asyncio
async def test_srr_context_injection(tmp_path):
    adapter_mock = AsyncMock(spec=SocraticodeGatewayAdapter)
    adapter_mock.semantic_search.return_value = {
        "status": "READY",
        "results": [{"vault_id": "v1", "score": 0.9, "summary": "test"}],
        "fallback_used": False
    }

    # Mocking vault file
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    (vault_path / "v1.json").write_text(json.dumps({
        "vault_id": "v1", "summary": "Full text of v1", "content_hash": "h1"
    }))

    resolver = VaultContextResolver(vault_path=vault_path)
    runtime = SemanticRetrievalRuntime(socraticode_adapter=adapter_mock, vault_resolver=resolver)

    res = await runtime.retrieve_for_prompt("hello")

    assert res["status"] == "READY"
    assert "v1" in res["vault_refs"]
    assert "# Retrieved DUMMIE Memory" in res["prompt_context_block"]
    assert "Full text of v1" in res["prompt_context_block"]

@pytest.mark.asyncio
async def test_srr_budget_application(tmp_path):
    adapter_mock = AsyncMock()
    adapter_mock.semantic_search.return_value = {
        "status": "READY",
        "results": [{"vault_id": "v1"}, {"vault_id": "v2"}, {"vault_id": "v3"}]
    }

    # Mock files
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    for i in range(1, 4):
        (vault_path / f"v{i}.json").write_text(json.dumps({
            "vault_id": f"v{i}", "summary": f"Note {i}", "content_hash": f"h{i}"
        }))

    budget_mock = MagicMock()
    budget_mock.summarize_budget_pressure.return_value = {"pressure": "high"}
    budget_mock.check_budget.return_value = {"ratio": 0.9} # High pressure

    resolver = VaultContextResolver(vault_path=vault_path)
    runtime = SemanticRetrievalRuntime(adapter_mock, context_budget_manager=budget_mock, vault_resolver=resolver)

    res = await runtime.retrieve_for_prompt("hello")

    assert res["budget_pressure"] == "HIGH"
    assert len(res["vault_refs"]) == 2 # Truncated from 3 to 2
    assert "v3" in res["dropped_refs"]
