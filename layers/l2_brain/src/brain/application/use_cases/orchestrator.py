import json
from brain.application.ports import BrainInputPort, ShieldOutputPort
from brain.domain.fabrication.models import AgentIntent, IntentType
from brain.domain.context.models import Vector6D, AuthorityLevel

class CognitiveOrchestrator(BrainInputPort):
    def __init__(self, shield_port: ShieldOutputPort):
        self.shield_port = shield_port

    async def handle_task(self, payload: str) -> str:
        print(f"[L2-Brain Orchestrator] Procesando tarea: {payload}")
        
        # Simulación de extracción de intención y contexto
        intent = AgentIntent(
            intent_type=IntentType.DELETE_FILE if "VETO" in payload else IntentType.READ_FILE,
            target="/",
            rationale="Mantenimiento sistémico",
            risk_score=0.9 if "VETO" in payload else 0.1
        )
        
        context = Vector6D(
            x=0.0, y=0.0, z=0.0, t=1, w=0.5, a=AuthorityLevel.AGENT
        )
        
        # Auditar intención con el Escudo (L3) a través del Output Port
        audit_result = self.shield_port.audit_intent(intent.model_dump_json())
        
        if not audit_result.get("authorized"):
            print(f"[L2-Brain Orchestrator] !!! VETO DEL ESCUDO (L3) !!! Motivo: {audit_result.get('shield_note')}")
            return "VETO_L3_SECURITY_VIOLATION"
            
        print(f"[L2-Brain Orchestrator] Intención autorizada por L3: {audit_result.get('shield_note')}")
        
        # TODO: Orquestar Memoria, Fabricación y Gobernanza.
        
        return "INTENT_QUEUED_L2_VALIDATED"
