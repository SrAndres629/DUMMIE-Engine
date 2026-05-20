# Spec: 152_cognitive_frame_builder
# Spec: DE-V2-L2-152

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any

@dataclass
class CognitiveFrame:
    frame_id: str
    intent: str
    operating_mode: str = "answer"
    must_preserve: List[str] = field(default_factory=list)
    should_include: List[str] = field(default_factory=list)
    must_not_include: List[str] = field(default_factory=list)
    mental_model_refs: List[str] = field(default_factory=list)
    memory_refs: List[str] = field(default_factory=list)
    ontology_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    token_budget_hint: str = "low"
    context_strategy: str = "MANIFEST_ONLY"
    dispatch_recommendation: str = "local"
    risks: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self): return asdict(self)

def build_cognitive_frame(intent: str, model=None, ontology=None) -> CognitiveFrame:
    frame_id = f"frame-{uuid.uuid4().hex[:8]}"
    must_preserve = ["current_phase", "sovereign_identity"]
    evidence_refs = []
    risks = []
    
    if model:
        evidence_refs.extend(getattr(model, "evidence_refs", []))
        risks.extend(getattr(model, "risks", []))
        if "TechnicalDebt" in getattr(model, "entities", []):
            must_preserve.append("technical_debt_refs")
    
    # Dispatch Logic
    dispatch = "local"
    if "refactor" in intent.lower() or "implementation" in intent.lower():
        dispatch = "antigravity"
    elif len(risks) > 3:
        dispatch = "human_review"

    return CognitiveFrame(
        frame_id=frame_id,
        intent=intent,
        must_preserve=must_preserve,
        mental_model_refs=[model.model_id] if model else [],
        ontology_refs=ontology.get("classes", []) if ontology else [],
        evidence_refs=evidence_refs,
        risks=risks,
        dispatch_recommendation=dispatch,
        must_not_include=["secrets", "private_chain_of_thought"]
    )
