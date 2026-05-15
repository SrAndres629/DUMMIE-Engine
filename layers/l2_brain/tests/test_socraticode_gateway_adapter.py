import pytest
from unittest.mock import AsyncMock, MagicMock
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter

@pytest.mark.asyncio
async def test_sga_mcp_success():
    mcp_mock = AsyncMock()
    mcp_mock.call_tool.return_value = {"results": [{"id": "v1", "score": 0.9, "summary": "test"}]}
    
    adapter = SocraticodeGatewayAdapter(mcp_gateway=mcp_mock)
    res = await adapter.semantic_search("test query")
    
    assert res["status"] == "READY"
    assert res["fallback_used"] is False
    assert len(res["results"]) == 1
    assert res["results"][0]["source"] == "mcp"

@pytest.mark.asyncio
async def test_sga_fallback_success():
    mcp_mock = AsyncMock()
    mcp_mock.call_tool.side_effect = Exception("MCP Offline")
    
    fallback_mock = MagicMock()
    fallback_mock.search_similar.return_value = [{"vault_id": "v2", "score": 0.8, "summary": "fb"}]
    
    adapter = SocraticodeGatewayAdapter(mcp_gateway=mcp_mock, fallback_index=fallback_mock)
    res = await adapter.semantic_search("test query")
    
    assert res["status"] == "DEGRADED"
    assert res["fallback_used"] is True
    assert len(res["results"]) == 1
    assert res["results"][0]["source"] == "fallback"

@pytest.mark.asyncio
async def test_sga_total_failure():
    adapter = SocraticodeGatewayAdapter()
    res = await adapter.semantic_search("test query")
    
    assert res["status"] == "FAILED"
    assert res["fallback_used"] is False
    assert len(res["results"]) == 0
