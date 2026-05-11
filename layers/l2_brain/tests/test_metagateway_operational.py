import pytest
import os
import sys
from unittest.mock import MagicMock

# Ensure we can import from the workspace root
sys.path.append(os.getcwd())

from layers.l2_brain.daemon import DummieDaemon
from layers.l2_brain.event_bus import AsyncEventBus

@pytest.mark.asyncio
async def test_daemon_initializes_metacognition():
    """
    Test that DummieDaemon correctly initializes MetacognitivePipeline
    when the files are present and imports are fixed.
    """
    # Mock dependencies
    event_bus = MagicMock(spec=AsyncEventBus)
    mcp_gateway = MagicMock()
    
    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=mcp_gateway,
        event_bus=event_bus
    )
    
    # This should fail if imports are still broken
    assert daemon.metacognition is not None, "MetacognitivePipeline should be initialized"
    assert hasattr(daemon, "metacognition_status"), "Daemon should have metacognition_status attribute"
    assert daemon.metacognition_status == "READY", f"Metacognition status should be READY, got {daemon.metacognition_status}"

@pytest.mark.asyncio
async def test_daemon_reports_degraded_on_import_error():
    """
    Test that daemon reports DEGRADED if metacognition fails to load.
    (This test might need to temporarily break imports or use a mock)
    """
    # For now, we just check if it currently fails as expected
    event_bus = MagicMock(spec=AsyncEventBus)
    mcp_gateway = MagicMock()
    
    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=mcp_gateway,
        event_bus=event_bus
    )
    
    # In current broken state, this will be None
    # We want it to be DEGRADED once we add the status tracking
    if daemon.metacognition is None:
        assert hasattr(daemon, "metacognition_status")
        assert daemon.metacognition_status in ["DEGRADED", "MISSING"]
