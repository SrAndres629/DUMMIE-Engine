import asyncio
import json
from unittest.mock import MagicMock
from layers.l2_brain.daemon import DummieDaemon
from layers.l2_brain.event_bus import AsyncEventBus

async def run_metacognitive_analyze_tool():
    event_bus = MagicMock(spec=AsyncEventBus)
    mcp_gateway = MagicMock()
    
    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=mcp_gateway,
        event_bus=event_bus
    )
    
    # Simulate calling the tool via the internal method
    result = await daemon._execute_local_reasoning(
        target="local.dummie_metacognitive_analyze",
        arguments={"raw_input": "Necesito refactorizar el gateway"}
    )
    
    print(f"Tool Result: {json.dumps(result, indent=2)}")
    assert "status" in result or "raw" in result

if __name__ == "__main__":
    asyncio.run(run_metacognitive_analyze_tool())
