from enum import Enum

class AuthorityLevel(str, Enum):
    """
    [CANONICAL] Niveles de Autoridad del DUMMIE Engine.
    Define la jerarquía de permisos y soberanía en el espacio cognitivo.
    """
    UNSPECIFIED = "AUTHORITY_UNSPECIFIED"
    AGENT = "AGENT"
    ENGINEER = "ENGINEER"
    ARCHITECT = "ARCHITECT"
    OVERSEER = "OVERSEER"
    HUMAN = "HUMAN"
