# Spec: DE-V2-L2-106
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ModelExpertise(str, Enum):
    CODING = "CODE"
    REASONING = "REASONING"
    GENERAL = "GENERAL"
    VISION = "VISION"
    TOOL_USE = "TOOL_USE"
    FAST_INFERENCE = "FAST_INFERENCE"

class ModelCapability(BaseModel):
    model_id: str
    expertise: List[ModelExpertise]
    context_window: int
    max_output_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    provider: str  # e.g., "ollama", "openai", "anthropic"
    is_local: bool = False
    latency_score: float = 0.5  # 0.0 to 1.0 (lower is faster)
    
class CapabilityRegistry(BaseModel):
    available_models: Dict[str, ModelCapability] = Field(default_factory=dict)
    default_model: str = "general-v1"

    def register_model(self, cap: ModelCapability):
        self.available_models[cap.model_id] = cap

    def get_best_model_for(self, expertise: ModelExpertise) -> Optional[ModelCapability]:
        # Simple heuristic: find fastest/cheapest for expertise
        candidates = [m for m in self.available_models.values() if expertise in m.expertise]
        if not candidates:
            return self.available_models.get(self.default_model)
        
        # Sort by cost and then latency
        candidates.sort(key=lambda x: (x.cost_per_1k_input, x.latency_score))
        return candidates[0]
