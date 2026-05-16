
import uuid
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

def get_utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

@dataclass
class MentalModel:
    model_id: str
    intent: str
    task_type: str
    entities: List[str] = field(default_factory=list)
    relations: List[Dict[str, str]] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)
    ontology_classes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: float = 0.0
    contradictions: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    context_strategy: str = "ALLOW_MANIFEST_ONLY"
    memory_refs: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=get_utc_now)
    quality_score: float = 0.0
    quality_findings: List[str] = field(default_factory=list)
    # Pack 5.2 Philosophical fields
    epistemic_state_ref: str = ""
    dialectical_review_ref: str = ""
    bias_findings: List[Dict[str, Any]] = field(default_factory=list)
    teleology: Dict[str, Any] = field(default_factory=dict)
    falsification_tests: List[str] = field(default_factory=list)
    belief_revision: str = ""

    def to_dict(self): return asdict(self)

def build_mental_model_for_intent(intent: str, task_type: str = "unknown", aiwg_root: Path = Path(".aiwg")) -> MentalModel:
    model_id = f"mm-{uuid.uuid4().hex[:8]}"
    entities = []
    relations = []
    risks = []
    assumptions = []
    evidence_refs = []
    contradictions = []
    decisions = []
    
    reports_root = aiwg_root / "reports"
    
    # Evidence Collection
    evidence_map = {
        "technical_debt": reports_root / "test_debt_triage_latest.json",
        "readiness": reports_root / "readiness_score_calibration_latest.json",
        "entrypoint": reports_root / "entrypoint_enforcement_audit_latest.json",
        "memory": reports_root / "memory_spine_entrypoint_latest.json"
    }
    
    for key, path in evidence_map.items():
        if path.exists():
            evidence_refs.append(str(path.relative_to(aiwg_root.parent)))
            try:
                data = json.loads(path.read_text())
                if key == "technical_debt":
                    entities.append("TechnicalDebt")
                    if data.get("failed_count", 0) > 0:
                        risks.append(f"Technical debt: {data.get('failed_count')} failing tests")
                if key == "readiness":
                    entities.append("ReadinessScore")
                    if any(f.get("id") == "score_1_with_degraded_kuzu" for f in data.get("findings", [])):
                        risks.append("Memory spine DEGRADED (Kuzu persistence unavailable)")
            except:
                pass

    # Basic entity/relation extraction from intent
    if "refactor" in intent.lower(): 
        entities.append("RefactorTarget")
        relations.append({"source": "RefactorTarget", "target": "TechnicalDebt", "type": "mitigates"})
    
    if "memory" in intent.lower():
        entities.append("MemoryContext")
        relations.append({"source": "MemoryContext", "target": "MemorySpine", "type": "consumes"})

    # Philosophical Logic (Pack 5.2)
    if "refactor" in intent.lower():
        assumptions.append("Target codebase is stable enough for modification")
        decisions.append("Audit technical debt report before execution")
        contradictions.append("Claim: PASS while 177 tests are missing")
    
    teleology = {"goal": intent, "impact_type": "architectural_integrity"}
    falsification_tests = [f"verify {intent} with 0 new regressions"]

    # Quality Calculation (Hardened 5.2)
    score = 100
    if not relations: score -= 20
    if not risks: score -= 10
    if not evidence_refs: score -= 30
    if not assumptions: score -= 10
    if any("DEGRADED" in str(r) for r in risks): score = min(score, 70) # Penalty for overconfidence

    return MentalModel(
        model_id=model_id,
        intent=intent,
        task_type=task_type,
        entities=list(set(entities)),
        relations=relations,
        risks=risks,
        assumptions=assumptions,
        decisions=decisions,
        evidence_refs=evidence_refs,
        contradictions=contradictions,
        confidence=0.9 if evidence_refs else 0.5,
        quality_score=max(0, score),
        teleology=teleology,
        falsification_tests=falsification_tests,
        created_at=get_utc_now()
    )
