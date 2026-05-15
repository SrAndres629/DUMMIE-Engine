import asyncio
import os
import sys
import time
import json

sys.path.append('layers/l1_nervous')
from tools_impl.swarm import register_swarm_tools
from utils import AtomicLedgerWriter

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

async def run_benchmark():
    mcp = MockFastMCP()
    root_dir = "/app"
    register_swarm_tools(mcp, MockUseCases(), root_dir)

    observe_swarm = mcp.tools['observe_swarm']

    AIWG_DIR = os.path.join(root_dir, ".aiwg")
    ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")

    # We measure how much this blocks the event loop
    async def background_task():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        return time.perf_counter() - start

    # Warm up
    await observe_swarm()

    # Baseline
    results = []
    blocks = []
    for _ in range(5):
        bg = asyncio.create_task(background_task())
        await asyncio.sleep(0.001)

        start = time.perf_counter()
        await observe_swarm()
        end = time.perf_counter()

        bg_time = await bg

        results.append(end - start)
        blocks.append(bg_time)

    avg_time = sum(results) / len(results)
    avg_block = sum(blocks) / len(blocks)

    pass pass # print(f"Average observe_swarm execution time: {avg_time:.5f}s")
    pass pass # print(f"Average event loop blockage for 10ms task: {avg_block:.5f}s")

if __name__ == '__main__':
    asyncio.run(run_benchmark())
