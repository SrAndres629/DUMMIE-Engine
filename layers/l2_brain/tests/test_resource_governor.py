import pytest
import asyncio
from unittest.mock import patch, MagicMock

from layers.l2_brain.structural_hardening.resource_governor import ResourceGovernor

@pytest.fixture
def governor():
    return ResourceGovernor(threshold_warning=0.8, threshold_critical=0.95)

@pytest.mark.asyncio
async def test_governor_healthy_state(governor):
    # Simulate low memory usage (50%)
    with patch.object(governor, '_read_cgroup_memory_ratio', return_value=0.5):
        decision = await governor.evaluate_system_health()
        assert decision["status"] == "HEALTHY"
        assert decision["recommended_concurrency"] >= 5

@pytest.mark.asyncio
async def test_governor_critical_state_throttles(governor):
    # Simulate critical memory usage (98%)
    with patch.object(governor, '_read_cgroup_memory_ratio', return_value=0.98):
        decision = await governor.evaluate_system_health()
        assert decision["status"] == "CRITICAL"
        assert decision["recommended_concurrency"] <= 1
        assert decision["action"] == "THROTTLE"

@pytest.mark.asyncio
async def test_governor_detects_idle_ollama(governor):
    # Simulate 15 minutes of idle time
    governor.last_active_time = asyncio.get_event_loop().time() - 900
    with patch.object(governor, '_unload_ollama') as mock_unload:
        await governor.evaluate_idle_timeout()
        mock_unload.assert_called_once()
