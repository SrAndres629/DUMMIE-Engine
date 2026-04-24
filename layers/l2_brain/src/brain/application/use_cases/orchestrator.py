import json
import hashlib
from datetime import datetime
from typing import Optional, List, Union
from brain.application.interfaces import IBrainOrchestrator
from brain.application.use_cases.crystallization import CrystallizeProceduralMemoryUseCase
from brain.application.use_cases.lessons_use_case import CrystallizeLessonsUseCase
from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
from brain.domain.memory.ports import IEventStorePort, ILedgerAuditPort, IShieldOutputPort, ISkillRepositoryPort, ISessionLedgerPort
from brain.domain.memory.models import MemoryNode4DTES, EgoState
from brain.domain.governance.models import DecisionRecord

class CognitiveOrchestrator(IBrainOrchestrator):
    """
    Orquestador Cognitivo (L2 Brain).
    Implementa el flujo determinista de la Spec 21 y Spec 42.
    """
    def __init__(
        self, 
        shield_port: IShieldOutputPort, 
        event_store: IEventStorePort,
        ledger_audit: ILedgerAuditPort,
        session_ledger: ISessionLedgerPort,
        skill_repo: ISkillRepositoryPort,
        mode: str = "GREENFIELD"
    ):
        self.shield = shield_port
        self.event_store = event_store
        self.ledger_audit = ledger_audit
        self.session_ledger = session_ledger
        self.skill_repo = skill_repo
        self.mode = mode
        # Recuperar el tick máximo del Event Store (Spec 02 - Causal Ordering)
        # Esto previene la destrucción del ordenamiento causal tras reinicios.
        self.lamport_clock = self._recover_lamport_clock()
        
        self.crystallize_use_case = CrystallizeProceduralMemoryUseCase(
            event_store=event_store,
            skill_repo=skill_repo,
            ledger_audit=ledger_audit
        )
        self.lessons_use_case = CrystallizeLessonsUseCase(
            ledger_audit=ledger_audit
        )

    def _recover_lamport_clock(self) -> int:
        """Recupera el tick máximo del 4D-TES para garantizar monotonía causal (Spec 02)."""
        try:
            result = self.event_store.conn.execute(
                "MATCH (m:MemoryNode4D) RETURN max(m.lamport_t)"
            )
            if result.has_next():
                max_tick = result.get_next()[0]
                if max_tick is not None:
                    return int(max_tick)
        except Exception as e:
            print(f"[L2-Brain Orchestrator] Warning: Could not recover Lamport clock: {e}")
        return 0

    async def handle_task(self, payload: Union[str, AgentIntent]) -> str:
        """
        Punto de entrada principal (Spec 21).
        Coordina el flujo de memoria, gobernanza y ejecución.
        """
        try:
            if isinstance(payload, AgentIntent):
                intent = payload
                print(f"[L2-Brain Orchestrator] Procesando intención directa: {intent.intent_type}")
            else:
                print(f"[L2-Brain Orchestrator] Procesando tarea en modo {self.mode}: {payload}")
                # 1. Parsing de Intención (Spec 21)
                intent = self._parse_intent(payload)
            
            # 2. Auditoría Metacognitiva de Certeza (Spec 42)
            # Bloquear mutaciones si la certeza del locus es baja (< 0.5)
            stats = self.ledger_audit.get_certainty_for_locus(intent.locus_x)
            if stats.certainty_score < 0.5 and intent.intent_i == ContextIntent.MUTATION:
                raise Exception(f"[Spec 42] Ontological lock: Certeza insuficiente ({stats.certainty_score}) para mutación en {intent.locus_x}")

            # 3. Análisis de Impacto (Spec 31)
            impact = self.event_store.compute_blast_radius(intent.target)
            
            # 4. Shielding (L3 - Spec 04)
            shield_result = self.shield.audit_intent(intent.model_dump_json())
            if not shield_result.get("authorized", False):
                return "INTENT_REJECTED_BY_SHIELD"

            # 5. Causal Chaining (4D-TES - Spec 02)
            parent_hash = self.event_store.get_last_leaf_hash(intent.locus_x)
            self.lamport_clock += 1
            
            node = MemoryNode4DTES(
                causal_hash=self._compute_hash(intent, parent_hash),
                parent_hash=parent_hash,
                payload=intent.rationale,
                payload_hash=hashlib.sha256(intent.rationale.encode()).hexdigest(),
                context=SixDimensionalContext(
                    locus_x=intent.locus_x,
                    locus_y=intent.target,
                    locus_z="L2_BRAIN",
                    lamport_t=self.lamport_clock,
                    authority_a=intent.authority_a,
                    intent_i=intent.intent_i
                )
            )
            self.event_store.append(node)
            print(f"[L2-Brain Orchestrator] Nodo 4D-TES encadenado: {node.causal_hash} (parent: {parent_hash})")

            # 6. Registro en el Ledger de Decisiones (Spec 34)
            self.ledger_audit.record_decision(DecisionRecord(
                decision_id=f"DEC-{self.lamport_clock}",
                tick=self.lamport_clock,
                context=node.context,
                rationale=intent.rationale,
                impact_blast_radius=impact["impact_level"],
                target_causal_hash=node.causal_hash,
                witness_hash=hashlib.sha256(node.causal_hash.encode()).hexdigest(), # Mock Sentinel
                metadata={"impact_details": impact}
            ))

            # 7. Registro en Session Ledger (Spec 36)
            self.session_ledger.record_ego_state(EgoState(
                agent_id="sw.plant.orchestrator",
                tick=self.lamport_clock,
                thought_vector=f"Handled task: {intent.rationale}",
                action="TASK_HANDLED",
                context=node.context
            ))

            return "INTENT_QUEUED_L2_VALIDATED"
        except Exception as e:
            # AUTO-CRISTALIZACIÓN DE LECCIONES (Spec 48)
            print(f"[L2-Brain Orchestrator] CRITICAL ERROR: {e}")
            
            # Intentar capturar el contexto para la lección
            context_fallback = SixDimensionalContext(
                locus_x="sw.plant.orchestrator",
                locus_y="L2_BRAIN",
                locus_z="L2_BRAIN",
                lamport_t=self.lamport_clock,
                authority_a=AuthorityLevel.OVERSEER,
                intent_i=ContextIntent.OBSERVATION
            )
            
            self.lessons_use_case.execute_error(
                context=context_fallback,
                error=e,
                tick=self.lamport_clock
            )
            raise e

    def _parse_intent(self, task: str) -> AgentIntent:
        """Heurística simple para mapear texto a intención estructurada."""
        # En producción, esto usaría un LLM o un Parser DSL
        return AgentIntent(
            intent_type=FabricationIntent.READ_FILE,
            target="/",
            rationale=task,
            risk_score=0.1
        )

    def _compute_hash(self, intent: AgentIntent, parent_hash: str) -> str:
        """Computa el hash causal incluyendo rationale para unicidad (Spec 02)."""
        content = f"{intent.intent_type}{intent.target}{parent_hash}{self.lamport_clock}{intent.rationale}"
        return hashlib.sha256(content.encode()).hexdigest()
