import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from layers.l2_brain.metagateway_adapter import MetaGatewayAdapter
from layers.l2_brain.sensor_first_guard import SensorFirstGuard
from layers.l2_brain.metagateway_runtime_meter import MetaGatewayRuntimeMeter
from layers.l2_brain.metagateway_policy import PolicyDecision

@pytest.mark.asyncio
async def test_metagateway_adapter_supports_call_tool():
    mock_gateway = MagicMock()
    mock_gateway.call_tool = AsyncMock(return_value={"content": [{"type": "text", "text": '{"capabilities": [{"id": "tool1"}]}'}]})
    
    adapter = MetaGatewayAdapter(mock_gateway)
    result = await adapter.discover_capabilities("find tools")
    
    assert result["success"] is True
    assert result["capabilities"][0]["id"] == "tool1"
    mock_gateway.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_metagateway_adapter_supports_execute_tool():
    mock_gateway = MagicMock()
    del mock_gateway.call_tool # Ensure only execute_tool is available
    mock_gateway.execute_tool = AsyncMock(return_value={"capabilities": [{"id": "tool2"}]})
    
    adapter = MetaGatewayAdapter(mock_gateway)
    result = await adapter.discover_capabilities("find more tools")
    
    assert result["success"] is True
    assert result["capabilities"][0]["id"] == "tool2"
    mock_gateway.execute_tool.assert_called_once()

def test_sensor_first_guard_logic():
    guard = SensorFirstGuard(mode=PolicyDecision.BLOCK)
    
    # Discovery without prior work -> BLOCK
    result = guard.evaluate_direct_read("concept_discovery", False, False)
    assert result["decision"] == "BLOCK"
    assert "Violation" in result["reason"]
    
    # Discovery with gateway -> ALLOW
    result = guard.evaluate_direct_read("concept_discovery", False, True)
    assert result["decision"] == "ALLOW"
    
    # Debug error -> ALLOW
    result = guard.evaluate_direct_read("debug_error", False, False)
    assert result["decision"] == "ALLOW"

def test_runtime_meter_token_reduction():
    meter = MetaGatewayRuntimeMeter()
    
    # Simulate some activity
    meter.record_gateway_usage(2000, "discovery")
    meter.record_gateway_usage(3200, "analysis")
    meter.record_direct_read(1000, "line_confirmation")
    meter.record_direct_read(2000, "debug_error")
    
    stats = meter.get_stats()
    assert stats["direct_read_attempts"] == 2
    assert stats["gateway_attempts"] == 2
    # Actual tokens: context = 3000 // 4 = 750, gateway = 5200 // 4 = 1300
    assert stats["actual_direct_tokens"] == 750
    assert stats["actual_gateway_tokens"] == 1300
    # Since actual_direct_tokens > 0 (750) and actual_gateway_tokens (1300), saved = 0. ratio = 0.0
    assert stats["token_reduction_ratio"] == 0.0
