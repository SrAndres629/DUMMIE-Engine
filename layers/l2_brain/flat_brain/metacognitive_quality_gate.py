# Spec: 155_metacognitive_quality_gate
# Spec: DE-V2-L2-155
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
    intent = getattr(model, "intent", "").lower()
    is_high_risk = any(k in intent for k in ["autonom", "synthesis", "kuzu", "degrad", "missing", "risk"])
    is_advisory = any(k in intent for k in ["what should i do next", "status", "help", "capabilities", "backlog", "readiness", "debt", "benchmark"])
    
    if is_advisory and not is_high_risk:
        return MetacognitiveQualityGateResult(
            decision="PASS",
            quality_score=100.0,
            findings=[],
            warnings=[],
            epistemic_debt_count=0,
            bias_count=0
        )

    findings = []
    warnings = []
    score = 100

    # 1. Model Checks
    relations = getattr(model, "relations", [])
    if not getattr(model, "entities", []):
        score -= 20
        findings.append({"category": "MODEL", "message": "No entities extracted", "severity": "WARN"})
    if not relations:
        score -= 20
        findings.append({"category": "MODEL", "message": "No relations extracted", "severity": "WARN" if not is_high_risk else "FAIL"})
    if not getattr(model, "evidence_refs", []):
        score -= 20
        findings.append({"category": "MODEL", "message": "No evidence references", "severity": "WARN"})
    
    # 2. Ontology Checks
    graph = ontology.get("ontology_graph", {}) if isinstance(ontology, dict) else getattr(ontology, "nodes", [])
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    if not edges:
        score -= 20
        findings.append({"category": "ONTOLOGY", "message": "Ontology graph is empty or has zero edges", "severity": "FAIL" if is_high_risk else "WARN"})
        
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
    bias_fail = False
    if bias_report:
        bias_decision = getattr(bias_report, "decision", "") if not isinstance(bias_report, dict) else bias_report.get("decision", "")
        b_findings = getattr(bias_report, "findings", []) if not isinstance(bias_report, dict) else bias_report.get("findings", [])
        b_count = len(b_findings)
        
        if bias_decision == "FAIL" or b_count > 0:
            bias_fail = True
            score -= 20 * max(1, b_count)
            findings.append({"category": "BIAS", "message": f"Found {b_count} cognitive biases", "severity": "FAIL"})

    # 5. Overconfidence and Degradation Caps (Pack 5.2.1 specific constraints)
    risks = getattr(model, "risks", [])
    kuzu_degraded = any("DEGRADED" in str(r) for r in risks) or "kuzu" in intent
    
    # Quality score cannot be above 70 while Kuzu is DEGRADED and 177 missing tests remain
    if kuzu_degraded:
        score = min(score, 70)
        findings.append({"category": "BIAS", "message": "Overconfidence penalty: Kuzu is DEGRADED", "severity": "WARN"})

    # Quality score cannot be above 50 if bias_report is FAIL
    if bias_fail:
        score = min(score, 50)
        findings.append({"category": "BIAS", "message": "Overconfidence penalty: bias report is FAIL", "severity": "FAIL"})

    # 6. Final Decision logic matching safety constraints
    decision = "PASS"
    
    # FAIL if bias_report decision is FAIL and action is autonomy/scaling
    if bias_fail and any(k in intent for k in ["autonom", "synthesis", "scale", "flywheel"]):
        decision = "FAIL"
        findings.append({"category": "SAFETY", "message": "Critical safety rejection: Autonomy requested while bias is FAIL", "severity": "FAIL"})
    # FAIL if ontology graph has zero edges and is high-risk
    elif not edges and is_high_risk:
        decision = "FAIL"
        findings.append({"category": "SAFETY", "message": "Critical safety rejection: Ontology graph has zero edges for high-risk intent", "severity": "FAIL"})
    # FAIL if mental model relations are empty for complex intent
    elif not relations and is_high_risk:
        decision = "FAIL"
        findings.append({"category": "SAFETY", "message": "Critical safety rejection: Mental model relations are empty for high-risk intent", "severity": "FAIL"})
    # FAIL if any finding has FAIL severity
    elif any(f["severity"] == "FAIL" for f in findings):
        decision = "FAIL"
    elif score < 40:
        decision = "FAIL"
    elif score < 70:
        decision = "NEEDS_HUMAN_REVIEW"
    elif score < 90:
        # PASS_WITH_WARNINGS if Kuzu degraded but action is only local/advisory repair
        if kuzu_degraded and not any(k in intent for k in ["autonom", "synthesis"]):
            decision = "PASS_WITH_WARNINGS"
        else:
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
