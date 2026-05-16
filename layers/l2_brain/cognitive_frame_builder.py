
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List

@dataclass
class CognitiveFrame:
    frame_id: str
    intent: str
    operating_mode: str = "answer"
    must_preserve: List[str] = field(default_factory=list)
    mental_model_refs: List[str] = field(default_factory=list)
    memory_refs: List[str] = field(default_factory=list)
    ontology_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    dispatch_recommendation: str = "local"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self): return asdict(self)

def build_cognitive_frame(intent: str, model=None, ontology=None) -> CognitiveFrame:
    return CognitiveFrame(
        frame_id=f"frame-{uuid.uuid4().hex[:8]}",
        intent=intent,
        mental_model_refs=[model.model_id] if model else [],
        ontology_refs=ontology.get("classes", []) if ontology else [],
        dispatch_recommendation="local" if "refactor" not in intent else "antigravity"
    )
