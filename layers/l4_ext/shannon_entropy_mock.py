
import math
from typing import List

def shannon_entropy(probabilities: List[float]) -> float:
    """Calcula la entropía de Shannon."""
    return -sum(p * math.log2(p) for p in probabilities if p > 0)
