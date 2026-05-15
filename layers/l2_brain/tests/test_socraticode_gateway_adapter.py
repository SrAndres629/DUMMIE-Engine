import pytest
from unittest.mock import AsyncMock, MagicMock
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter

@pytest.mark.asyncio
async def test_sga_mcp_call_tool_success():
    mcp_mock = AsyncMock()
    # Mocking a gateway that has both call_tool and execute_tool
    mcp_mock.call_tool.return_value = {"results": [{"id": "v1", "score": 0.9, "summary": "test"}]}

    adapter = SocraticodeGatewayAdapter(mcp_gateway=mcp_mock)
    res = await adapter.semantic_search("test query")

    assert res["status"] == "READY"
    assert res["adapter_method_used"] == "call_tool"
    assert len(res["results"]) == 1

@pytest.mark.asyncio
async def test_sga_mcp_execute_tool_fallback():
    mcp_mock = AsyncMock()
    # call_tool fails, execute_tool succeeds
    mcp_mock.call_tool.side_effect = Exception("call_tool failed")
    mcp_mock.execute_tool.return_value = {"results": [{"id": "v1", "score": 0.9, "summary": "test"}]}

    adapter = SocraticodeGatewayAdapter(mcp_gateway=mcp_mock)
    res = await adapter.semantic_search("test query")

    assert res["status"] == "READY"
    assert res["adapter_method_used"] == "execute_tool"
    assert len(res["results"]) == 1

@pytest.mark.asyncio
async def test_sga_index_fallback():
    mcp_mock = AsyncMock()
    mcp_mock.call_tool.side_effect = Exception("all mcp failed")
    mcp_mock.execute_tool.side_effect = Exception("all mcp failed")

    fallback_mock = MagicMock()
    fallback_mock.search_similar.return_value = [{"vault_id": "v2", "score": 0.8, "summary": "fb"}]

    adapter = SocraticodeGatewayAdapter(mcp_gateway=mcp_mock, fallback_index=fallback_mock)
    res = await adapter.semantic_search("test query")

    assert res["status"] == "DEGRADED"
    assert res["adapter_method_used"] == "fallback_index"
    assert res["fallback_used"] is True
