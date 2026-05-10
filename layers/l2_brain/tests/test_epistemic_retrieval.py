import pytest
import time
import json
from layers.l2_brain.domain.retrieval_service import RetrievalService, EpistemicNode

def test_epistemic_scoring_baseline():
    node = EpistemicNode(
        causal_hash="hash1",
        parent_hashes=["hash0"],
        payload="plain text payload",
        payload_hash="p_hash1",
        lamport_t=int(time.time()),
        authority_a="AGENT",
        intent_i="MUTATION"
    )
    score = RetrievalService.calculate_epistemic_score(node, query_sim=0.5)
    # El cálculo debe ejecutarse sin fallar sobre payloads planos (retrocompatibilidad)
    assert isinstance(score, float)

def test_epistemic_scoring_structured():
    structured_payload = json.dumps({
        "content": "Refactor memory engine",
        "pi_confidence": 0.9,
        "rho_risk": 0.1,
        "evidence_hashes": ["hash0", "hash_evidence"]
    })
    
    node = EpistemicNode(
        causal_hash="hash2",
        parent_hashes=["hash1"],
        payload=structured_payload,
        payload_hash="p_hash2",
        lamport_t=int(time.time()),
        authority_a="HUMAN", # Mayor peso de autoridad
        intent_i="MUTATION"
    )
    
    score_human = RetrievalService.calculate_epistemic_score(node, query_sim=0.8)
    
    node_agent = EpistemicNode(
        causal_hash="hash3",
        parent_hashes=["hash1"],
        payload=structured_payload,
        payload_hash="p_hash3",
        lamport_t=int(time.time()),
        authority_a="AGENT",
        intent_i="MUTATION"
    )
    
    score_agent = RetrievalService.calculate_epistemic_score(node_agent, query_sim=0.8)
    
    # El nodo del Humano debe puntuar más alto por peso de autoridad
    assert score_human > score_agent

def test_node_ranking_order():
    nodes = [
        EpistemicNode(
            causal_hash="h1",
            parent_hashes=["h0"],
            payload_hash="ph1",
            lamport_t=int(time.time()),
            intent_i="FABRICATION",
            payload=json.dumps({"content": "a", "pi_confidence": 0.2}), # Baja confianza
            authority_a="AGENT"
        ),
        EpistemicNode(
            causal_hash="h2",
            parent_hashes=["h0"],
            payload_hash="ph2",
            lamport_t=int(time.time()),
            intent_i="FABRICATION",
            payload=json.dumps({"content": "b", "pi_confidence": 0.9}), # Alta confianza
            authority_a="ARCHITECT"
        )
    ]
    
    ranked = RetrievalService.rank_nodes(nodes, query_similarities=[0.5, 0.5])
    assert ranked[0].causal_hash == "h2"

def test_extract_minimal_proof_subgraph():
    # Mocking a graph
    db = {
        "h1": EpistemicNode(
            causal_hash="h1", parent_hashes=["GENESIS"],
            payload=json.dumps({"content": "A", "pi_confidence": 1.0}), authority_a="HUMAN", lamport_t=int(time.time()), intent_i="FABRICATION", payload_hash="ph1"
        ),
        "h2": EpistemicNode(
            causal_hash="h2", parent_hashes=["h1"],
            payload=json.dumps({"content": "B", "pi_confidence": 0.5}), authority_a="AGENT", lamport_t=int(time.time()), intent_i="FABRICATION", payload_hash="ph2"
        )
    }
    
    def mock_get(h):
        return db.get(h)
        
    start_node = db["h2"]
    
    # Con tau alto (por ejemplo 1.5), debería extraer ambos nodos
    subgraph_high = RetrievalService.extract_minimal_proof_subgraph(start_node, mock_get, query_sim=1.0, tau_threshold=1.5)
    assert len(subgraph_high) == 2
    assert "h2" in [n.causal_hash for n in subgraph_high]
    assert "h1" in [n.causal_hash for n in subgraph_high]
    
    # Con tau muy bajo (0.1), debería detenerse en el primer nodo
    subgraph_low = RetrievalService.extract_minimal_proof_subgraph(start_node, mock_get, query_sim=1.0, tau_threshold=0.1)
    assert len(subgraph_low) == 1
    assert subgraph_low[0].causal_hash == "h2"
