import logging
from typing import Tuple
from layers.l2_brain.domain.authority import AuthorityLevel
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.shield.authority")

class AuthorityGate:
    def __init__(self):
        # El escudo ya no bloquea por defecto, ahora ESCALA según la soberanía
        self.sovereign_bypass = {
            AuthorityLevel.HUMAN,
            AuthorityLevel.OVERSEER,
            AuthorityLevel.ARCHITECT,
            AuthorityLevel.ENGINEER
        }

    async def validate_intent(self, frame: MetacognitiveFrame) -> Tuple[bool, str]:
        """
        Valida si la intención puede ejecutarse. 
        MANDATO: El modo Read-Only ha sido revocado. 
        Se permite la mutación si el nivel de autoridad es soberano.
        """
        lvl = frame.authority_level
        logger.info(f"Shield audit: Level={lvl} Intent={frame.raw_user_input[:30]}")
        
        # El nivel HUMAN es el override absoluto del creador
        if lvl == AuthorityLevel.HUMAN:
            return True, "SVRN_CONFIRM: Autoridad HUMAN detectada. Acceso total a mutación."

        # OVERSEER y ARCHITECT ahora tienen permiso de escritura por diseño soberano
        if lvl in {AuthorityLevel.OVERSEER, AuthorityLevel.ARCHITECT}:
            return True, f"SVRN_CONFIRM: Autoridad {lvl} habilitada para escritura y mutación políglota."
        
        if lvl == AuthorityLevel.ENGINEER:
            return True, "SVRN_CONFIRM: Nivel ENGINEER habilitado para refactor y optimización."
            
        if lvl == AuthorityLevel.AGENT:
            return True, "SVRN_DELEGATED: Nivel AGENT habilitado para operaciones de rutina."

        return False, f"VETO_L3: Nivel de autoridad '{lvl}' no reconocido o insuficiente para mutación."
