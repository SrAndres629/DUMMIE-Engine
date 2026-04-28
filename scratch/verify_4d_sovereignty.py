
import sys
import os
sys.path.append(os.path.abspath("layers/l2_brain"))
sys.path.append(os.path.abspath("layers/l1_nervous"))

from adapters import KuzuRepository
from models import MemoryNode4D, AuthorityLevel, IntentType
import time

DB_PATH = os.path.abspath(".aiwg/memory/loci.db")
print(f"Connecting to DB: {DB_PATH}")

try:
    repo = KuzuRepository(db_path=DB_PATH)
    # Si no falla aquí, el lock está libre o el IPC funciona.
    
    parent_hash = repo.get_last_leaf_hash()
    lamport_t = int(time.time() * 1000)
    
    payload = "VERIFICACIÓN DIRECTA: Motor 4D operativo sin gateway."
    
    causal_hash, cypher = MemoryNode4D.build_create_cypher(
        parent_hash=parent_hash,
        locus_x="direct.verification",
        locus_y="LOCAL",
        locus_z="L2_BRAIN",
        lamport_t=lamport_t,
        authority_a=AuthorityLevel.AGENT.value,
        intent_i=IntentType.CRYSTALLIZATION.value,
        payload=payload
    )
    
    repo.query(cypher)
    print(f"SUCCESS: Node crystallized with hash {causal_hash}")
    
    # Verificar lectura
    node = repo.get_by_hash(causal_hash)
    if node and node.payload == payload:
        print("VERIFICATION PASSED: Read-after-write success.")
    else:
        print("VERIFICATION FAILED: Could not read back node.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
