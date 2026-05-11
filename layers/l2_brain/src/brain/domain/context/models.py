from enum import Enum
from pydantic import BaseModel, Field
from typing import Tuple, List

class AuthorityLevel(str, Enum):
    AUTHORITY_UNSPECIFIED = "AUTHORITY_UNSPECIFIED"
    AGENT = "AGENT"
    ENGINEER = "ENGINEER"
    ARCHITECT = "ARCHITECT"
    OVERSEER = "OVERSEER"
    HUMAN = "HUMAN"

class IntentType(str, Enum):
    INTENT_UNSPECIFIED = "INTENT_UNSPECIFIED"
    OBSERVATION = "OBSERVATION"
    MUTATION = "MUTATION"
    RESOLUTION = "RESOLUTION"
    CRYSTALLIZATION = "CRYSTALLIZATION"

class SixDimensionalContext(BaseModel):
    """
    6D-Context Model (Spec 12)
    V = {x, y, z, t, a, i}
    Alineado con proto/dummie/v2/memory.proto
    """
    locus_x: str = Field(..., description="ID del Bounded Context")
    locus_y: str = Field(..., description="ID del Aggregate Root")
    locus_z: str = Field(..., description="ID de la Entidad Atómica")
    lamport_t: int = Field(..., ge=0, description="Contador monotónico local de causalidad")
    authority_a: AuthorityLevel = Field(AuthorityLevel.AGENT, description="Peso determinista")
    intent_i: IntentType = Field(..., description="Razón inmutable de existencia")

    def immutable_core(self) -> Tuple[str, str, str, int, str]:
        """Returns the immutable dimensions (x, y, z, t, i)"""
        return (self.locus_x, self.locus_y, self.locus_z, self.lamport_t, self.intent_i.value)

    def compute_context_hash(self) -> str:
        """Helper para el cálculo de CausalHash"""
        import hashlib
        core_str = f"{self.locus_x}|{self.locus_y}|{self.locus_z}|{self.lamport_t}|{self.intent_i.value}|{self.authority_a.value}"
        return hashlib.sha256(core_str.encode('utf-8')).hexdigest()
