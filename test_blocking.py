import asyncio
import time
import os
import json

async def run():
    async def bg():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        return time.perf_counter() - start

    # Run background first, but give it a bit of time to start so we catch the blockage
    t1 = asyncio.create_task(bg())
    await asyncio.sleep(0.001)

    start = time.perf_counter()
    with open("/app/.aiwg/memory/swarm_ledger.jsonl", "r") as f:
        lines = f.readlines()[-10:]
    end = time.perf_counter()
    b_time = await t1
    print(f"Sync read time: {end - start:.5f}s, bg task: {b_time:.5f}s (blockage: {b_time - 0.01:.5f}s)")

    t1 = asyncio.create_task(bg())
    await asyncio.sleep(0.001)
    start = time.perf_counter()

    def read_lines():
        with open("/app/.aiwg/memory/swarm_ledger.jsonl", "r") as f:
            return f.readlines()[-10:]

    lines = await asyncio.to_thread(read_lines)
    end = time.perf_counter()
    b_time = await t1
    print(f"Async to_thread read time: {end - start:.5f}s, bg task: {b_time:.5f}s (blockage: {b_time - 0.01:.5f}s)")

asyncio.run(run())
