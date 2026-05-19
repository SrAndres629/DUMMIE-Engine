import pytest
import asyncio
import os
import time

from layers.l1_nervous.tools_impl.swarm import register_swarm_tools
from layers.l1_nervous.utils import AtomicLedgerWriter

class MockOrchestrator:
    lamport_clock = 0

class MockUseCases:
    orchestrator = MockOrchestrator()

class MockFastMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

@pytest.mark.asyncio
async def test_observe_swarm_perf_behavior(tmp_path):
    mcp = MockFastMCP()
    root_dir = str(tmp_path)
    os.makedirs(os.path.join(root_dir, ".aiwg", "memory"), exist_ok=True)
    
    register_swarm_tools(mcp, MockUseCases(), root_dir)
    observe_swarm = mcp.tools['observe_swarm']

    start = time.perf_counter()
    result = await observe_swarm()
    end = time.perf_counter()

    assert end - start < 1.0, "observe_swarm should be fast"
    assert result is not None, "observe_swarm should return a result"
    
    # Assuming observe_swarm returns string or dict containing swarm status
    assert len(result) > 0, "Result should not be empty"
