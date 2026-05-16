
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

    def to_dict(self): return asdict(self)

def build_mental_model_for_intent(intent: str, task_type: str = "unknown") -> MentalModel:
    model_id = f"mm-{uuid.uuid4().hex[:8]}"
    entities = []
    if "refactor" in intent.lower(): entities.append("TechnicalDebt")
    if "memory" in intent.lower(): entities.append("MemorySpine")
    
    return MentalModel(
        model_id=model_id,
        intent=intent,
        task_type=task_type,
        entities=entities,
        evidence_refs=[".aiwg/reports/technical_debt_intelligence_latest.json"],
        confidence=0.7 if entities else 0.5,
        semantic_tags=["runtime", "metacognition"]
    )
