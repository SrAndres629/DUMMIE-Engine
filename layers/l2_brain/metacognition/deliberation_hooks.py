import logging
import json
from typing import Any, List, Dict
from .contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.deliberation_hooks")

class MissionDecomposerHook:
    def __init__(self, daemon: Any):
        self.daemon = daemon

    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        if frame.refined_intent == "OBJECTIVE_INQUIRY":
             frame.mission_plan = [{"step": 1, "agent": "ObserverAgent", "action": "Gather system intel"}]
             return frame

        prompt = f"""
        Genera un plan de misión estructurado en JSON para el siguiente objetivo:
        "{frame.raw_user_input}"
        
        Razonamiento previo: {frame.deliberation_summary}
        
        Devuelve SOLO un array JSON de objetos con esta estructura:
        [
          {{"step": 1, "agent": "nombre_agente", "action": "descripcion_accion"}},
          ...
        ]
        """
        
        result_text = await self.daemon.reason_with_tiers(
            prompt=prompt,
            system_prompt="Eres un arquitecto de enjambres (Swarm Architect). Responde solo con JSON válido.",
            concept="mission_decomposition",
            saga_id=frame.session_id
        )
        
        try:
            # Limpiar posibles backticks de markdown
            json_str = result_text.strip().replace("```json", "").replace("```", "").strip()
            frame.mission_plan = json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse mission plan JSON: {e}")
            frame.mission_plan = [{"step": 1, "agent": "FallbackAgent", "action": "Manual intervention required"}]
            
        return frame

class PlanCriticHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        # Self-critique logic
        if not frame.mission_plan:
            frame.deliberation_summary = "CRITIQUE: Mission plan is empty. Fallback required."
        else:
            frame.deliberation_summary = f"CRITIQUE: Plan with {len(frame.mission_plan)} steps accepted."
        return frame
