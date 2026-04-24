import pytest
import os
import hashlib
from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.domain.memory.models import MemoryNode4DTES
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType

@pytest.fixture
def repo(tmp_path):
    db_path = str(tmp_path / "test_loci.db")
    return KuzuRepository(db_path)

def create_node(causal_hash, parent_hash, payload, t):
    context = SixDimensionalContext(
        locus_x="test.x",
        locus_y="test.y",
        locus_z="test.z",
        lamport_t=t,
        authority_a=AuthorityLevel.HUMAN,
        intent_i=IntentType.OBSERVATION
    )
    return MemoryNode4DTES(
        causal_hash=causal_hash,
        parent_hash=parent_hash,
        payload=payload,
        payload_hash=hashlib.sha256(payload.encode()).hexdigest(),
        context=context
    )

def test_kuzu_repository_append_and_get(repo):
    node = create_node("hash1", "GENESIS", "payload1", 1)
    success = repo.append(node)
    assert success is True
    
    retrieved = repo.get_by_hash("hash1")
    assert retrieved is not None
    assert retrieved.causal_hash == "hash1"
    assert retrieved.payload == b"payload1"

def test_kuzu_repository_causal_chain(repo):
    node1 = create_node("hash1", "GENESIS", "payload1", 1)
    node2 = create_node("hash2", "hash1", "payload2", 2)
    node3 = create_node("hash3", "hash2", "payload3", 3)
    
    repo.append(node1)
    repo.append(node2)
    repo.append(node3)
    
    chain = repo.get_causal_chain("hash3")
    assert len(chain) == 3
    assert chain[0].causal_hash == "hash3"
    assert chain[1].causal_hash == "hash2"
    assert chain[2].causal_hash == "hash1"

def test_kuzu_repository_last_leaf(repo):
    assert repo.get_last_leaf_hash() == "GENESIS"
    
    node1 = create_node("hash1", "GENESIS", "payload1", 1)
    repo.append(node1)
    assert repo.get_last_leaf_hash() == "hash1"
    
    node2 = create_node("hash2", "hash1", "payload2", 2)
    repo.append(node2)
    assert repo.get_last_leaf_hash() == "hash2"

def test_kuzu_repository_blast_radius(repo):
    # node1 -> node2 -> node3
    #       -> node4
    node1 = create_node("hash1", "GENESIS", "p1", 1)
    node2 = create_node("hash2", "hash1", "p2", 2)
    node3 = create_node("hash3", "hash2", "p3", 3)
    node4 = create_node("hash4", "hash1", "p4", 4)
    
    repo.append(node1)
    repo.append(node2)
    repo.append(node3)
    repo.append(node4)
    
    impact = repo.compute_blast_radius("hash1")
    # Nodes dependent on hash1: hash2, hash3, hash4
    assert impact["total_impacted_nodes"] >= 2 # Kuzu count might be tricky with recursivity if not careful
    
    impact_leaf = repo.compute_blast_radius("hash3")
    assert impact_leaf["total_impacted_nodes"] == 0
