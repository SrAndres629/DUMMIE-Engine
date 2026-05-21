from __future__ import annotations
import numpy as np
from typing import List, Protocol

class EmbeddingProvider(Protocol):
    def generate_vector(self, text: str) -> List[float]: ...
    def similarity(self, v1: List[float], v2: List[float]) -> float: ...

class CanonicalEmbeddingAdapter:
    """
    Adaptador formal para la generación y comparación de embeddings.
    Cumple con el contrato de infraestructura de L2_Brain.
    """
    def __init__(self, generator_fn):
        self.generator_fn = generator_fn

    def generate_vector(self, text: str) -> List[float]:
        return self.generator_fn(text)

    def similarity(self, v1: List[float], v2: List[float]) -> float:
        a, b = np.array(v1), np.array(v2)
        if not np.any(a) or not np.any(b):
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
