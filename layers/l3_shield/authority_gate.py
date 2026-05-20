import logging
from typing import Tuple
try:
    from metacognition.contracts import AuthorityLevel, MetacognitiveFrame
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "l2_brain")))
    from metacognition.contracts import AuthorityLevel, MetacognitiveFrame

logger = logging.getLogger("dummie.shield.authority")

class AuthorityGate:
    def __init__(self):
        self.restricted_levels = {
            AuthorityLevel.ARCHITECT,
            AuthorityLevel.OVERSEER
        }

    async def validate_intent(self, frame: MetacognitiveFrame) -> Tuple[bool, str]:
        """
        Valida si la intención puede ejecutarse según el nivel de autoridad.
        """
        logger.info(f"Shield validating authority level: {frame.authority_level}")
        
        if frame.authority_level == AuthorityLevel.OVERSEER:
            return False, "VETO_L3: Acción crítica de nivel OVERSEER requiere veto humano presencial."
        
        if frame.authority_level == AuthorityLevel.ARCHITECT:
            # En un sistema real, aquí verificaríamos tokens de aprobación persistente
            return False, "PENDING_L3: Acción externa de nivel ARCHITECT requiere confirmación del usuario."
            
        return True, "CONFIRM_L3: Autoridad delegada aceptada."
