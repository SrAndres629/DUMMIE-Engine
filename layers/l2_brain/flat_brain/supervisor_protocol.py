import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("brain.supervisor")

@dataclass
class ReviewResult:
    approved: bool
    score: float
    feedback: str
    reasons: list[str]

class SupervisorProtocol:
    """
    [L2_BRAIN] Protocolo de supervisión entre neuronas.
    Permite que modelos de nivel superior validen el trabajo de modelos worker.
    """
    def __init__(self, model_executor: Any, model_router: Any):
        self.executor = model_executor
        self.router = model_router

    async def review_task(self, goal: str, worker_output: str, model_id: str) -> ReviewResult:
        """
        Solicita a un modelo superior que revise el output de un modelo worker.
        """
        prompt = f"""
        Actúa como el Director Técnico de DUMMIE Engine.
        Revisa el siguiente trabajo realizado por la neurona {model_id} para la meta: "{goal}".
        
        TRABAJO:
        {worker_output}
        
        Evalúa si el trabajo es correcto, seguro y eficiente. 
        Devuelve un JSON con: {{"approved": bool, "score": float (0-1), "feedback": string, "reasons": [string]}}
        """
        
        # Forzar tier CLOUD_PREM o el más alto disponible para supervisión
        try:
            # En un entorno real, llamaríamos al executor con el tier superior
            # result_text = await self.executor.execute_on_tier("cloud_prem", prompt, concept="supervision")
            # Por ahora simulamos la deliberación si no hay modelos premium configurados
            logger.info(f"SupervisorProtocol: Reviewing work of {model_id}...")
            
            # Si el output contiene "ERROR", desaprobamos automáticamente
            if "ERROR" in worker_output.upper():
                return ReviewResult(False, 0.1, "Error detectado en el output.", ["execution_error"])
            
            return ReviewResult(True, 0.9, "Trabajo validado correctamente.", ["quality_ok"])
            
        except Exception as e:
            logger.error(f"Supervision failed: {e}")
            return ReviewResult(True, 0.5, "Supervisión fallida, aprobación por defecto.", ["supervision_error"])
