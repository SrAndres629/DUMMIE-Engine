import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

# Setup path
sys.path.append(os.path.abspath("layers/l1_nervous"))
sys.path.append(os.path.abspath("layers/l2_brain"))

from bootstrap import bootstrap_orchestrator

# Test
db_path = os.path.abspath(".aiwg/memory/loci.db")
aiwg_dir = os.path.abspath(".aiwg")

print(f"Testing with DB: {db_path}")
orchestrator = bootstrap_orchestrator(db_path, aiwg_dir)
print(f"Read only? {orchestrator.event_store.read_only}")

if not orchestrator.event_store.read_only:
    # Test connection
    try:
        res = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)")
        count = 0
        if hasattr(res, "get_next"):
            count = res.get_next()[0]
        elif hasattr(res, "has_next"):
            while res.has_next():
                count = res.get_next()[0]
        else:
            for row in res:
                count = row[0]
        print(f"Nodes: {count}")
    except Exception as e:
        print(f"Query Error: {e}")

