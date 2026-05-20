# Spec: 156_epistemic_state_runtime
# Spec: DE-V2-L2-156
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict

@dataclass
class EpistemicState:
    decision: str
    claims: List[Dict[str, Any]] = field(default_factory=list)
    knowns: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    epistemic_debts: List[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_refs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self): return asdict(self)

def build_epistemic_state(intent: str, aiwg_root: Path = Path(".aiwg")) -> EpistemicState:
    reports_root = aiwg_root / "reports"
    knowns = []
    unknowns = []
    assumptions = []
    contradictions = []
    debts = []
    confidence = 1.0
    evidence_refs = []
    
    # 1. Check Kuzu Physical Reality
    readiness_path = reports_root / "readiness_score_calibration_latest.json"
    if readiness_path.exists():
        evidence_refs.append(str(readiness_path.relative_to(aiwg_root.parent)))
        data = json.loads(readiness_path.read_text())
        findings = data.get("findings", [])
        if any(f.get("id") == "score_1_with_degraded_kuzu" for f in findings):
            contradictions.append("Kuzu claim: PASS vs Reality: DEGRADED findings in readiness report")
            debts.append("Unresolved graph persistence (Kuzu)")
            confidence -= 0.4

    # 2. Check Test Reality
    test_path = reports_root / "test_debt_triage_latest.json"
    if test_path.exists():
        data = json.loads(test_path.read_text())
        knowns.append(f"Technical debt: {data.get('failed_count')} failing tests")
        if data.get("failed_count", 0) > 0:
            confidence -= 0.2

    # 3. Handle Intent unknowns
    if "refactor" in intent.lower():
        assumptions.append("Refactor target exists and is documented")
        unknowns.append("Full side-effect graph of refactor")

    decision = "PASS"
    if confidence < 0.5: decision = "FAIL"
    elif confidence < 0.9: decision = "PASS_WITH_WARNINGS"

    return EpistemicState(
        decision=decision,
        knowns=knowns,
        unknowns=unknowns,
        assumptions=assumptions,
        contradictions=contradictions,
        epistemic_debts=debts,
        confidence=max(0.0, confidence),
        evidence_refs=evidence_refs,
        warnings=["Unresolved epistemic debt" if debts else ""]
    )
