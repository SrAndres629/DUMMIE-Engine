import logging
import json
from typing import Any
from .contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.reasoning_hooks")

class ReasoningExpansionHook:
    def __init__(self, daemon: Any):
        self.daemon = daemon

    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        """
        Expande el pensamiento sobre el objetivo usando razonamiento multinivel.
        """
        logger.info(f"Expanding reasoning for objective: {frame.strategic_objective}")
        
        prompt = f"""
        Actúa como el Cerebro Metacognitivo de DUMMIE.
        Objetivo del usuario: {frame.raw_user_input}
        Intención detectada: {frame.refined_intent}
        Objetivo estratégico: {frame.strategic_objective}
        
        Produce un resumen deliberativo verificable para cumplir este objetivo.
        No expongas cadena de pensamiento privada. Incluye:
        1. Dependencias técnicas.
        2. Riesgos de seguridad.
        3. Herramientas necesarias.
        4. Pasos de verificación.
        5. Hipótesis consideradas y criterios de decisión.
        
        Devuelve un resumen de deliberación claro y profesional.
        """
        
        # Usamos el sistema de tiers del daemon para delegar a un modelo local (LOCAL_DEEP) si es posible
        reasoning = await self.daemon.reason_with_tiers(
            prompt=prompt,
            system_prompt=(
                "Eres el módulo estratégico de DUMMIE Engine. "
                "Devuelve solo un resumen operacional verificable, sin razonamiento privado."
            ),
            concept="metacognitive_expansion",
            saga_id=frame.session_id
        )
        
        frame.deliberation_summary = reasoning
        logger.info("Reasoning expansion completed.")
        return frame
