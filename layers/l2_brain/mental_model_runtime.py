
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

    def to_dict(self): return asdict(self)

def build_mental_model_for_intent(intent: str, task_type: str = "unknown", aiwg_root: Path = Path(".aiwg")) -> MentalModel:
    model_id = f"mm-{uuid.uuid4().hex[:8]}"
    entities = []
    relations = []
    risks = []
    assumptions = []
    evidence_refs = []
    contradictions = []
    
    reports_root = aiwg_root / "reports"
    
    # Evidence Collection
    evidence_map = {
        "technical_debt": reports_root / "test_debt_triage_latest.json",
        "readiness": reports_root / "readiness_score_calibration_latest.json",
        "entrypoint": reports_root / "entrypoint_enforcement_audit_latest.json",
        "memory": reports_root / "memory_spine_entrypoint_latest.json",
        "token": reports_root / "token_economy_benchmark_latest.json"
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
                    score = data.get("readiness_score", 0)
                    if score < 70:
                        risks.append(f"Low readiness score: {score}%")
                if key == "memory":
                    entities.append("MemorySpine")
                    if data.get("status") == "DEGRADED_WITH_FILE_BACKED_MEMORY":
                        risks.append("Memory spine DEGRADED (file-backed fallback)")
            except:
                pass

    # Basic entity extraction from intent
    if "refactor" in intent.lower(): 
        entities.append("RefactorTarget")
        relations.append({"source": "RefactorTarget", "target": "TechnicalDebt", "type": "mitigates"})
    
    if "memory" in intent.lower():
        entities.append("MemoryContext")
        relations.append({"source": "MemoryContext", "target": "MemorySpine", "type": "consumes"})

    # Risks from Working Tree (Hardening 5.1)
    try:
        import subprocess
        status = subprocess.check_output("git status --short", shell=True).decode().strip()
        if status:
            risks.append("Dirty working tree detected")
            relations.append({"source": "Runtime", "target": "WorkingTree", "type": "degrades"})
    except:
        pass

    # Contradictions
    if "PASS" in intent.upper() and risks:
        contradictions.append("Intent claims PASS but risks are present")

    # Quality Calculation
    score = 100
    findings = []
    if not relations: 
        score -= 20
        findings.append("No relations extracted")
    if not risks:
        score -= 10
        findings.append("No risks identified")
    if not evidence_refs:
        score -= 30
        findings.append("No evidence-backed reports found")
    
    return MentalModel(
        model_id=model_id,
        intent=intent,
        task_type=task_type,
        entities=list(set(entities)),
        relations=relations,
        risks=risks,
        assumptions=assumptions,
        evidence_refs=evidence_refs,
        contradictions=contradictions,
        confidence=0.9 if evidence_refs else 0.5,
        quality_score=max(0, score),
        quality_findings=findings,
        created_at=get_utc_now()
    )

if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "test refactor"
    model = build_mental_model_for_intent(intent)
    print(json.dumps(model.to_dict(), indent=2))
