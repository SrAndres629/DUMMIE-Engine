from enum import Enum
from pydantic import BaseModel, Field
from typing import Tuple

class AuthorityLevel(str, Enum):
    HUMAN = "HUMAN"
    OVERSEER = "OVERSEER"
    ARCHITECT = "ARCHITECT"
    ENGINEER = "ENGINEER"
    AGENT = "AGENT"

class Vector6D(BaseModel):
    """
    6D-Context Model (Spec 12)
    V = {x, y, z, t, w, a}
    """
    # Spatial Dimensions
    x: float = Field(..., description="Eje X: Dimensión espacial 1")
    y: float = Field(..., description="Eje Y: Dimensión espacial 2")
    z: float = Field(..., description="Eje Z: Dimensión espacial 3")
    
    # Temporal Dimension
    t: int = Field(..., description="Eje t: Reloj de Lamport (Tiempo lógico)")
    
    # Semantic Relevance
    w: float = Field(..., ge=0.0, le=1.0, description="Eje w: Relevancia semántica [0.0, 1.0]")
    
    # Authority Level
    a: AuthorityLevel = Field(..., description="Eje a: Nivel de autoridad")

    def immutable_core(self) -> Tuple[float, float, float, int]:
        """Returns the immutable dimensions (x, y, z, t)"""
        return (self.x, self.y, self.z, self.t)

    def is_highly_relevant(self) -> bool:
        return self.w > 0.8
