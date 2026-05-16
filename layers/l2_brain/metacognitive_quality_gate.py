
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class MetacognitiveQualityFinding:
    category: str
    message: str
    severity: str  # WARN, FAIL

@dataclass
class MetacognitiveQualityGateResult:
    decision: str  # PASS, PASS_WITH_WARNINGS, FAIL, NEEDS_HUMAN_REVIEW
    quality_score: float
    findings: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    epistemic_debt_count: int = 0
    bias_count: int = 0

    def to_dict(self): return asdict(self)

def run_metacognitive_quality_gate(model, ontology, frame, epistemic=None, bias_report=None) -> MetacognitiveQualityGateResult:
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
    graph = ontology.get("ontology_graph", {}) if isinstance(ontology, dict) else getattr(ontology, "nodes", [])
    if not graph:
        score -= 10
        findings.append({"category": "ONTOLOGY", "message": "Ontology graph is empty", "severity": "WARN"})
        
    # 3. Epistemic Checks
    ep_debt_count = 0
    if epistemic:
        ep_debt_count = len(epistemic.epistemic_debts)
        if ep_debt_count > 0:
            score -= 15 * ep_debt_count
            findings.append({"category": "EPISTEMIC", "message": f"Found {ep_debt_count} epistemic debts", "severity": "WARN"})
        if epistemic.confidence < 0.7:
            score -= 20
            findings.append({"category": "EPISTEMIC", "message": "Low epistemic confidence", "severity": "WARN"})

    # 4. Bias Checks
    b_count = 0
    if bias_report:
        b_count = len(bias_report.findings)
        if b_count > 0:
            score -= 20 * b_count
            findings.append({"category": "BIAS", "message": f"Found {b_count} cognitive biases", "severity": "FAIL"})

    # 5. Overconfidence Penalty
    risks = getattr(model, "risks", [])
    if any("DEGRADED" in str(r) for r in risks) and score > 90:
        score = 70
        findings.append({"category": "BIAS", "message": "Overconfidence penalty: high score with degraded components", "severity": "WARN"})

    # 6. Final Decision
    decision = "PASS"
    if score < 40 or any(f["severity"] == "FAIL" for f in findings):
        decision = "FAIL"
    elif score < 70:
        decision = "NEEDS_HUMAN_REVIEW"
    elif score < 90:
        decision = "PASS_WITH_WARNINGS"
        warnings = [f["message"] for f in findings]
        
    return MetacognitiveQualityGateResult(
        decision=decision,
        quality_score=float(max(0, score)),
        findings=findings,
        warnings=warnings,
        epistemic_debt_count=ep_debt_count,
        bias_count=b_count
    )
