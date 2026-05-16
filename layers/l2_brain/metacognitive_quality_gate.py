
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class MetacognitiveQualityFinding:
    category: str
    message: str
    severity: str  # WARN, FAIL

@dataclass
class MetacognitiveQualityGateResult:
    decision: str  # PASS, PASS_WITH_WARNINGS, FAIL
    quality_score: float
    findings: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self): return asdict(self)

def run_metacognitive_quality_gate(model, ontology, frame) -> MetacognitiveQualityGateResult:
    findings = []
    warnings = []
    score = 100
    
    # 1. Model Checks
    if not getattr(model, "entities", []):
        score -= 20
        findings.append({"category": "MODEL", "message": "No entities extracted", "severity": "WARN"})
    if not getattr(model, "relations", []):
        score -= 20
        findings.append({"category": "MODEL", "message": "No relations extracted", "severity": "WARN"})
    if not getattr(model, "evidence_refs", []):
        score -= 20
        findings.append({"category": "MODEL", "message": "No evidence references", "severity": "WARN"})
    
    # 2. Ontology Checks
    graph = ontology.get("ontology_graph", {})
    if not graph.get("nodes"):
        score -= 10
        findings.append({"category": "ONTOLOGY", "message": "Ontology graph has no nodes", "severity": "WARN"})
    if not graph.get("edges"):
        score -= 10
        findings.append({"category": "ONTOLOGY", "message": "Ontology graph has no edges", "severity": "WARN"})
        
    # 3. Frame Checks
    if not getattr(frame, "must_preserve", []):
        score -= 10
        findings.append({"category": "FRAME", "message": "No preservation rules in frame", "severity": "WARN"})

    # 4. Critical Safety Checks (FAIL conditions)
    # Check for private reasoning patterns (simulated)
    # Check for secret patterns (simulated)
    
    decision = "PASS"
    if score < 50:
        decision = "FAIL"
    elif score < 90:
        decision = "PASS_WITH_WARNINGS"
        warnings = [f["message"] for f in findings]
        
    return MetacognitiveQualityGateResult(
        decision=decision,
        quality_score=float(score),
        findings=findings,
        warnings=warnings
    )
