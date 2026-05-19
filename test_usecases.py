import os
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.path.abspath("layers/l2_brain/flat_brain"))
sys.path.insert(0, os.path.abspath("layers/l2_brain"))
sys.path.insert(0, os.path.abspath("layers/l1_nervous"))
from bootstrap import bootstrap_orchestrator
from application.use_cases import BrainToolUseCases
from models import SixDimensionalContext, AuthorityLevel, IntentType

db_path = os.path.abspath(".aiwg/memory/loci.db")
aiwg_dir = os.path.abspath(".aiwg")

orchestrator = bootstrap_orchestrator(db_path, aiwg_dir)
use_cases = BrainToolUseCases(orchestrator, None)

async def test():
    print("--- Test Calibrate ---")
    results = []
    if getattr(orchestrator.event_store, "read_only", False) or getattr(orchestrator.event_store, "conn", None) is None:
        results.append("[!] Loci Graph: OFFLINE (Database locked or stub mode).")
    else:
        try:
            res = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)")
            node_count = res.get_next()[0] if hasattr(res, "get_next") else next(res)[0]
            results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected (Native Mode).")
        except Exception as e:
            results.append(f"[!] Loci Graph: ERROR ({e})")
    print("\n".join(results))

    print("--- Test Crystallize ---")
    ctx = {
        "locus_x": "test_x",
        "locus_y": "test_y",
        "locus_z": "test_z",
        "lamport_t": orchestrator.lamport_clock,
        "authority_a": "HUMAN",
        "intent_i": "FABRICATION",
    }
    res = await use_cases.execute_crystallization("test memory from script", ctx)
    print(f"Crystallize result: {res}")
    
    await asyncio.sleep(2) # Wait for daemon background task

    print("--- Test Verify ---")
    res = orchestrator.event_store.conn.execute("MATCH (n) RETURN n.payload LIMIT 1")
    payload = next(res)[0] if not hasattr(res, "get_next") else res.get_next()[0]
    print(f"Persisted payload: {payload}")

if __name__ == "__main__":
    asyncio.run(test())
