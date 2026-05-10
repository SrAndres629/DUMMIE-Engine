import json
from typing import List
from brain.domain.memory.ports import IEventStorePort, ISkillRepositoryPort
from brain.domain.memory.models import MemoryNode4DTES
from brain.application.use_cases.crystallization import CrystallizeProceduralMemoryUseCase

class KaizenLoopAgent:
    """
    Agente de Evolución Autónoma (Spec 27).
    Realiza ciclos de reflexión y destilación de conocimiento.
    """
    def __init__(
        self, 
        event_store: IEventStorePort,
        skill_repo: ISkillRepositoryPort,
        crystallizer: CrystallizeProceduralMemoryUseCase
    ):
        self.event_store = event_store
        self.skill_repo = skill_repo
        self.crystallizer = crystallizer

    async def run_reflection_cycle(self, locus_x: str) -> dict:
        """
        Analiza los últimos nodos de un locus para detectar patrones repetitivos.
        Si la certeza supera el umbral, cristaliza una Skill.
        """
        head = self.event_store.get_last_leaf_hash(locus_x=locus_x)
        if head == "GENESIS":
            return {"status": "SKIPPED", "reason": "No memory nodes found for locus"}
            
        chain = self.event_store.get_causal_chain(head)
        
        # Simulación de detección de patrón (Spec 27/28)
        # En una versión real, esto usaría un LLM para detectar regularidad.
        if len(chain) >= 3:
            # Intentar cristalización
            skill_id = f"SKILL-{locus_x.replace('.', '_').upper()}"
            source_hashes = [n.causal_hash for n in chain[-3:]]
            
            result = await self.crystallizer.execute(
                skill_id=skill_id,
                source_hashes=source_hashes,
                context=chain[-1].context
            )
            
            return {
                "status": "CRYSTALLIZED" if "skill_id" in result else "STABILIZING",
                "skill_id": result.get("skill_id"),
                "certainty": result.get("certainty_score", 0.0)
            }
            
        return {"status": "COLLECTING_DATA", "count": len(chain)}
