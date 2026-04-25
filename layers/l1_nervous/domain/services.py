import logging
from typing import Dict, Any, List
from .models import SixDimensionalContext, AgentIntent, AuthorityLevel, IntentType

logger = logging.getLogger("dummie.l1.domain.services")

class NervousDomainService:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def crystallize_knowledge(self, payload: str, context_data: Dict[str, Any]) -> str:
        """Business logic for persisting knowledge."""
        if getattr(self.orchestrator.event_store, "read_only", False):
            raise PermissionError("ERR_MEMORY_LOCKED: Modo lectura activo.")

        intent = AgentIntent(
            intent_type=IntentType.RESOLUTION,
            target="L2_BRAIN",
            rationale=f"Crystallization Request: {payload}",
            risk_score=0.1,
            authority_a=context_data.get("authority", AuthorityLevel.HUMAN),
            intent_i=IntentType.RESOLUTION,
            locus_x=context_data.get("locus", "sw.strategy.discovery")
        )
        
        # Mapping to the orchestrator's expected format if necessary
        result = await self.orchestrator.handle_task(intent)
        return f"Cristalización completada: {result}"

    def record_lesson(self, issue: str, correction: str):
        """Business logic for recording learned lessons."""
        if getattr(self.orchestrator.event_store, "read_only", False):
            raise PermissionError("ERR_MEMORY_LOCKED: Memoria bloqueada.")

        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery", locus_y="L1_TRANSPORT", locus_z="L2_BRAIN",
            lamport_t=self.orchestrator.lamport_clock, authority_a=AuthorityLevel.OVERSEER,
            intent_i=IntentType.OBSERVATION
        )
        
        self.orchestrator.lessons_use_case.execute_error(
            context=context, error=Exception(issue), tick=self.orchestrator.lamport_clock, correction=correction
        )
        return "Lección registrada exitosamente."
