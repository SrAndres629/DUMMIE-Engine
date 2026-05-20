from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class OptimizationAction(str, Enum):
    COMPRESS = "compress"
    QUANTIZE = "quantize"
    NONE = "none"

class CognitiveProfile(BaseModel):
    hard_limit: int = Field(default=32000, description="Límite máximo de tokens.")
    soft_threshold: int = Field(default=24000, description="Umbral para compresión.")
    
    def evaluate(self, current_tokens: int) -> OptimizationAction:
        if current_tokens >= self.hard_limit:
            return OptimizationAction.QUANTIZE
        elif current_tokens >= self.soft_threshold:
            return OptimizationAction.COMPRESS
        return OptimizationAction.NONE

class CapabilityRelevance(BaseModel):
    name: str
    score: float
    reason: Optional[str] = None
