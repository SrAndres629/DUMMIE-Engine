import math
from typing import Optional

try:
    from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
except ModuleNotFoundError:
    from domain.dtos import HypothesisBundle, Hypothesis

class HypothesisService:
    """
    Servicio de Dominio encargado de gestionar los Haces de Hipótesis (H_t)
    y calcular la entropía de Shannon para decidir cuándo colapsar la rama.
    """
    
    @staticmethod
    def calculate_entropy(bundle: HypothesisBundle) -> float:
        """
        Calcula la Entropía de Shannon H(w) = - \sum w_i * log2(w_i)
        Un H(w) cercano a 0 significa certeza absoluta (colapso).
        Un H(w) alto significa alta incertidumbre (mantener superposición).
        """
        bundle.normalize_weights()
        entropy = 0.0
        for h in bundle.hypotheses:
            if h.weight > 0:
                entropy -= h.weight * math.log2(h.weight)
        return entropy

    @staticmethod
    def should_collapse(bundle: HypothesisBundle, entropy_threshold: float = 0.5) -> bool:
        """
        Determina si el haz tiene la certidumbre suficiente para colapsar en una decisión.
        """
        if not bundle.hypotheses:
            return True
        if len(bundle.hypotheses) == 1:
            return True
        return HypothesisService.calculate_entropy(bundle) < entropy_threshold

    @staticmethod
    def collapse_to_dominant(bundle: HypothesisBundle) -> Optional[Hypothesis]:
        """
        Extrae la hipótesis más probable una vez que la entropía permite el colapso.
        """
        if not bundle.hypotheses:
            return None
        bundle.normalize_weights()
        return max(bundle.hypotheses, key=lambda h: h.weight)

    @staticmethod
    def update_weights_with_evidence(bundle: HypothesisBundle, evidence_impacts: dict):
        """
        Actualización Bayesiana de pesos de hipótesis basado en impactos de evidencia.
        evidence_impacts es un mapa de hypothesis_id -> multiplicador de verosimilitud.
        """
        for h in bundle.hypotheses:
            impact = evidence_impacts.get(h.hypothesis_id, 1.0)
            h.weight = max(0.0, h.weight * impact)
        bundle.normalize_weights()
