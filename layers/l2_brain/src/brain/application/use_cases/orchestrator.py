import json
import hashlib
from datetime import datetime
from typing import Any, Optional, List, Union
from brain.application.interfaces import IBrainOrchestrator
from brain.application.use_cases.crystallization import CrystallizeProceduralMemoryUseCase
from brain.application.use_cases.lessons_use_case import CrystallizeLessonsUseCase
from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
from brain.domain.memory.ports import IEventStorePort, ILedgerAuditPort, IShieldOutputPort, ISkillRepositoryPort, ISessionLedgerPort
from brain.domain.memory.models import MemoryNode4DTES, EgoState
from brain.domain.governance.models import DecisionRecord

from brain.domain.capability_registry import CapabilityRegistry, ModelExpertise
from brain.application.services.model_router import ModelRouterV2

class CognitiveOrchestrator(IBrainOrchestrator):
    """
    Orquestador Cognitivo (L2 Brain).
    Implementa el flujo determinista de la Spec 21 y Spec 42.
    Spec: DE-V2-L2-106, DE-V2-L2-200
    """
    def __init__(
        self, 
        shield_port: IShieldOutputPort, 
        event_store: IEventStorePort,
        ledger_audit: ILedgerAuditPort,
        session_ledger: ISessionLedgerPort,
        skill_repo: ISkillRepositoryPort,
        embedding_port: Optional["IEmbeddingPort"] = None,
        registry: Optional[CapabilityRegistry] = None,
        supervisor: Optional[Any] = None,
        sync_guard: Optional[Any] = None,
        mode: str = "GREENFIELD"
    ):
        self.shield = shield_port
        self.event_store = event_store
        self.ledger_audit = ledger_audit
        self.session_ledger = session_ledger
        self.skill_repo = skill_repo
        self.embedding_port = embedding_port
        self.registry = registry or CapabilityRegistry()
        self.supervisor = supervisor
        self.sync_guard = sync_guard
        self.router = ModelRouterV2(self.registry)
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
            return self.event_store.get_max_lamport_tick()
        except Exception:
            pass
        return 0

    def sync_clock(self, external_tick: int) -> None:
        """Sincroniza el Reloj de Lamport local con el pulso sistémico (Spec 03)."""
        if external_tick > self.lamport_clock:
            old_tick = self.lamport_clock
            self.lamport_clock = external_tick
            pass # print(f"[L2-Brain Orchestrator] Clock Synced: {old_tick} -> {self.lamport_clock}")

    async def handle_task(self, payload: Union[str, AgentIntent]) -> str:
        """
        Punto de entrada principal (Spec 21).
        Coordina el flujo de memoria, gobernanza y ejecución.
        """
        try:
            # 1. Parsing de Intención (Spec 21)
            if isinstance(payload, AgentIntent):
                intent = payload
            else:
                intent = self._parse_intent(payload)

            # 1b. Model Routing (Spec 106 - Pack 4.1)
            selected_model = self.router.route_intent(intent.intent_type)
            pass # print(f"[L2-Brain Orchestrator] Model selected for {intent.intent_type}: {selected_model.model_id if selected_model else 'DEFAULT'}")
            
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
                parent_hashes=[parent_hash] if parent_hash else ["GENESIS"],
                locus_x=intent.locus_x,
                locus_y=intent.target,
                locus_z="L2_BRAIN",
                lamport_t=self.lamport_clock,
                authority_a=str(intent.authority_a.value) if hasattr(intent.authority_a, "value") else str(intent.authority_a),
                intent_i=str(intent.intent_i.value) if hasattr(intent.intent_i, "value") else str(intent.intent_i),
                payload=intent.rationale,
                payload_hash=hashlib.sha256(intent.rationale.encode()).hexdigest(),
            )
            
            # 5b. Generar Embedding Semántico (Local-RAG)
            if self.embedding_port:
                node.embedding = await self.embedding_port.generate_embedding_async(intent.rationale)

            self.event_store.append(node)
            pass # print(f"[L2-Brain Orchestrator] Nodo 4D-TES encadenado: {node.causal_hash} (parent: {parent_hash})")

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
            pass # print(f"[L2-Brain Orchestrator] CRITICAL ERROR: {e}")
            
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

    async def process_intent(self, intent: Any) -> dict:
        """Bridge compatibility method for legacy caller contract (Spec 42)."""
        from brain.domain.fabrication.models import AgentIntent, IntentType
        from brain.domain.context.models import AuthorityLevel
        
        goal = getattr(intent, "goal", "")
        agent_intent = AgentIntent(
            intent_type=IntentType.READ_FILE,
            target="/",
            rationale=goal,
            risk_score=0.1,
            authority_a=AuthorityLevel.AGENT
        )
        status = await self.handle_task(agent_intent)
        
        try:
            last_hash = self.event_store.get_last_leaf_hash(agent_intent.locus_x)
        except Exception:
            last_hash = "LEGACY-01"
            
        return {
            "status": "ACK" if status == "INTENT_QUEUED_L2_VALIDATED" else "REJECTED",
            "intent_id": last_hash
        }
