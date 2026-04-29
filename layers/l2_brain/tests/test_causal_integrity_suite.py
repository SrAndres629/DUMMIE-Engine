import pytest
import hashlib
from layers.l2_brain.models import MemoryNode4D

def test_from_intent_context_is_callable():
    node = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="sw.strategy.discovery",
        locus_y="L1_TRANSPORT",
        locus_z="L2_BRAIN",
        lamport_t=1,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload="hello",
    )
    assert len(node.causal_hash) == 64
    assert node.parent_hashes == ["GENESIS"]

def test_canonical_hash_is_deterministic():
    node_a = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="sw.strategy.discovery",
        locus_y="L1_TRANSPORT",
        locus_z="L2_BRAIN",
        lamport_t=1,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload="hello",
    )
    node_b = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="sw.strategy.discovery",
        locus_y="L1_TRANSPORT",
        locus_z="L2_BRAIN",
        lamport_t=1,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload="hello",
    )
    assert node_a.causal_hash == node_b.causal_hash

def test_payload_with_quotes_does_not_break_cypher():
    node = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="sw.strategy.discovery",
        locus_y="L1_TRANSPORT",
        locus_z="L2_BRAIN",
        lamport_t=1,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload="O'Hara\nMATCH (x) DETACH DELETE x",
    )
    cypher = node.to_cypher()
    # Verifica que la comilla se escapó a \'Hara o ''Hara según cypher_literal
    assert "O\\'Hara" in cypher or "O''Hara" in cypher

def test_multiline_payload_round_trips_without_causal_integrity_failure(tmp_path):
    from layers.l2_brain.adapters import KuzuRepository

    repo = KuzuRepository(db_path=str(tmp_path / "loci"))
    node = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="sw.strategy.discovery",
        locus_y="L1_TRANSPORT",
        locus_z="L2_BRAIN",
        lamport_t=1,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload="line one\nline two",
    )

    repo.query(node.to_cypher())
    restored = repo.get_by_hash(node.causal_hash)

    assert restored.payload == node.payload
    assert restored.payload_hash == node.payload_hash

def test_invalid_hash_is_rejected():
    from layers.l2_brain.adapters import KuzuRepository
    # Mock connection
    class MockConn:
        def execute(self, query, params=None):
            class MockRes:
                def has_next(self): return False
            return MockRes()
    
    repo = KuzuRepository(db=None)
    repo.conn = MockConn()
    
    # SHA-256 válido
    repo.get_by_hash("a" * 64)
    
    # Hash no válido levantará ValueError
    with pytest.raises(ValueError):
        repo.get_by_hash("abc' OR 1=1")
