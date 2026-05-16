from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class PhilosophicalOntology:
    decision: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    dimensions: List[str]
    teleology: Dict[str, Any]
    authority_constraints: List[str]
    truth_constraints: List[str]
    risk_constraints: List[str]

    def to_dict(self): return asdict(self)

def build_philosophical_ontology(intent: str) -> PhilosophicalOntology:
    nodes = [
        {"id": "DUMMIE", "type": "AGENT", "role": "SOVEREIGN"},
        {"id": "KUZU", "type": "COMPONENT", "state": "DEGRADED"},
        {"id": "INTENT", "type": "TELEOLOGY", "goal": intent}
    ]
    edges = [
        {"source": "DUMMIE", "target": "KUZU", "type": "DEPENDS_ON"},
        {"source": "DUMMIE", "target": "INTENT", "type": "ACTS_TOWARDS"}
    ]
    return PhilosophicalOntology(
        decision="PASS",
        nodes=nodes,
        edges=edges,
        dimensions=["Being", "Teleology", "Agency"],
        teleology={"goal": intent, "impact": "evolution"},
        authority_constraints=["ADVISORY_ONLY"],
        truth_constraints=["EVIDENCE_BACKED_ONLY"],
        risk_constraints=["SAFETY_FIRST"]
    )
