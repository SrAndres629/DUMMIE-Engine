import pytest
from layers.l2_brain.adapters import KuzuRepository
from layers.l2_brain.models import MemoryNode4D, AuthorityLevel, IntentType

def test_graph_traversal(tmp_path):
    db_file = str(tmp_path / "test_db")
    repo = KuzuRepository(db_path=db_file)
    
    # 1. Crear nodo padre
    parent = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="x", locus_y="y", locus_z="z",
        lamport_t=1,
        authority_a=AuthorityLevel.AGENT,
        intent_i=IntentType.FABRICATION,
        payload="parent_content"
    )
    repo.create_memory_node(parent)
    
    # 2. Crear nodo hijo
    child = MemoryNode4D.from_intent_context(
        parent_hashes=[parent.causal_hash],
        locus_x="x", locus_y="y", locus_z="z",
        lamport_t=2,
        authority_a=AuthorityLevel.AGENT,
        intent_i=IntentType.FABRICATION,
        payload="child_content"
    )
    repo.create_memory_node(child)
    
    # 3. Verificar relación física CAUSAL_LINK en KùzuDB
    cypher = (
        "MATCH (p:MemoryNode4D)-[r:CAUSAL_LINK]->(c:MemoryNode4D) "
        "WHERE p.causal_hash = $p_hash AND c.causal_hash = $c_hash "
        "RETURN count(r)"
    )
    res = repo.query(cypher, {"p_hash": parent.causal_hash, "c_hash": child.causal_hash})
    
    assert res.has_next()
    count = res.get_next()[0]
    assert count == 1, f"Expected 1 CAUSAL_LINK, found {count}"
