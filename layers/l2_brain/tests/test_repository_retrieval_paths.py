from pathlib import Path

from layers.l2_brain.adapters import KuzuRepository
from layers.l2_brain.models import MemoryNode4D


def _persist(repo: KuzuRepository, node: MemoryNode4D) -> None:
    repo.query(node.to_cypher())


def test_repository_can_return_proof_subgraph_for_ranked_match(tmp_path: Path):
    repo = KuzuRepository(db_path=str(tmp_path / "retrieval.db"))

    parent = MemoryNode4D.from_intent_context(
        parent_hash="GENESIS",
        locus_x="test",
        locus_y="retrieval",
        locus_z="proof",
        lamport_t=1,
        authority_a="AGENT",
        intent_i="OBSERVATION",
        payload='{"content":"Parent evidence","pi_confidence":0.1,"rho_risk":0.9}',
    )
    child = MemoryNode4D.from_intent_context(
        parent_hash=parent.causal_hash,
        locus_x="test",
        locus_y="retrieval",
        locus_z="proof",
        lamport_t=2,
        authority_a="HUMAN",
        intent_i="RESOLUTION",
        payload='{"content":"Child decision","pi_confidence":0.6}',
    )

    _persist(repo, parent)
    _persist(repo, child)

    matches = repo.find_similar_nodes(
        "Child decision",
        limit=1,
        include_proof_subgraph=True,
        tau_threshold=1.5,
    )

    assert len(matches) == 1
    assert matches[0]["hash"] == child.causal_hash
    assert matches[0]["proof_subgraph"] == [child.causal_hash, parent.causal_hash]
    assert matches[0]["proof_size"] == 2
