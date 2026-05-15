import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from layers.l2_brain.daemon import DummieDaemon
from layers.l2_brain.gateway_contract import GatewayRequest

@pytest.mark.asyncio
async def test_daemon_runtime_truth_context_injection(tmp_path):
    # Setup mocks
    mcp_mock = AsyncMock()
    # Mocking semantic search to return a hit
    mcp_mock.call_tool.return_value = {
        "results": [{"id": "v1", "score": 0.9, "summary": "Resolved Memory Content"}]
    }
    
    # Setup vault file
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    (vault_path / "v1.json").write_text(json.dumps({
        "vault_id": "v1", "summary": "Resolved Memory Content", "content_hash": "h1"
    }))
    
    event_bus = MagicMock()
    model_router = MagicMock()
    model_executor = AsyncMock()
    
    # Initial decision - Cloud Std
    from layers.l2_brain.model_router import RoutingDecision, ModelTier, TaskComplexity
    model_router.route.return_value = RoutingDecision(
        tier=ModelTier.CLOUD_STD,
        complexity=TaskComplexity.ROUTINE,
        model_id="mock-cloud",
        reason="initial"
    )
    # Mock registry
    model_router.registry.models = {ModelTier.CLOUD_STD: [MagicMock(model_id="mock-cloud")]}
    
    daemon = DummieDaemon(
        ledger_path=str(tmp_path / "ledger.db"),
        mcp_gateway=mcp_mock,
        event_bus=event_bus,
        model_router=model_router,
        model_executor=model_executor
    )
    # Override vault resolver path
    daemon.semantic_retrieval_runtime.vault_resolver.vault_path = vault_path
    
    # Mock orchestrator to avoid full DAG execution
    daemon.orchestrator = AsyncMock()

    # 1. Process Request (This triggers retrieval and stores last_prompt_context_block)
    request = GatewayRequest(
        session_id="s1",
        goal="explain memory",
        dag_xml='<dag><task id="t1" tool="local.reasoning"/></dag>'
    )
    await daemon._process_request_safe(request)
    
    assert daemon.last_prompt_context_block != ""
    assert "Resolved Memory Content" in daemon.last_prompt_context_block
    
    # 2. Call reason_with_tiers (This should inject the block)
    await daemon.reason_with_tiers("What do you remember?")
    
    # Check that model_executor was called with the context block in system_prompt
    args, kwargs = model_executor.execute_config.call_args
    system_prompt_used = args[2] if len(args) > 2 else kwargs.get("system_prompt")
    
    assert "# Retrieved DUMMIE Memory" in system_prompt_used
    assert "Resolved Memory Content" in system_prompt_used
    
    # 3. Verify Context-Aware Routing (Router should have been called with hook_metadata)
    # The second call to route happens inside reason_with_tiers
    # router.route(prompt, hook_metadata=hook_metadata)
    # The first call was in _process_request_safe if we added it there (but we didn't yet in the daemon code, it was only in reason_with_tiers)
    
    call_args_list = model_router.route.call_args_list
    # Find the call from reason_with_tiers
    found_metadata = False
    for call in call_args_list:
        if "hook_metadata" in call.kwargs and call.kwargs["hook_metadata"]:
            metadata = call.kwargs["hook_metadata"]
            if metadata.get("retrieved_context_count", 0) > 0:
                found_metadata = True
                break
    
    assert found_metadata is True
