from pydantic import BaseModel, Field
from typing import List, Optional

class EpistemicPayload(BaseModel):
    """
    Representa el contexto epistémico de un nodo de memoria.
    Implementa el tuplo (c, pi, rho, delta, E).
    """
    content: str = Field(..., description="El contenido textual o representativo de la memoria.")
    pi_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Probabilidad/Confianza a priori.")
    rho_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Evaluación del riesgo.")
    delta_decay: float = Field(default=0.0, description="Decaimiento temporal acumulado.")
    evidence_hashes: List[str] = Field(default_factory=list, description="Soporte evidencial (Enlaces Merkle).")

class Hypothesis(BaseModel):
    """Representa una hipótesis individual en una rama de razonamiento."""
    hypothesis_id: str
    content: str
    weight: float = Field(default=1.0, ge=0.0)
    parent_hashes: List[str] = Field(default_factory=list)

class HypothesisBundle(BaseModel):
    """Haz de Hipótesis ponderadas (H_t) que evita el colapso prematuro del contexto."""
    bundle_id: str
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    
    def normalize_weights(self):
        total = sum(h.weight for h in self.hypotheses)
        if total > 0:
            for h in self.hypotheses:
                h.weight /= total
