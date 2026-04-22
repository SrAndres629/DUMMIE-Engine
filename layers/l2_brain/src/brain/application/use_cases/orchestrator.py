import json
from datetime import datetime
from brain.application.interfaces import IBrainOrchestrator
from brain.application.use_cases.crystallization import CrystallizeProceduralMemoryUseCase
from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
from brain.domain.memory.models import MemoryNode4DTES
from brain.domain.governance.models import DecisionRecord
from brain.domain.memory.ports import IEventStorePort, ILedgerAuditPort, IShieldOutputPort, ISkillRepositoryPort

class CognitiveOrchestrator(IBrainOrchestrator):
    def __init__(
        self, 
        shield_port: IShieldOutputPort, 
        event_store: IEventStorePort,
        ledger_audit: ILedgerAuditPort,
        skill_repo: ISkillRepositoryPort
    ):
        self.shield_port = shield_port
        self.event_store = event_store
        self.ledger_audit = ledger_audit
        self.skill_repo = skill_repo
        self.crystallizer = CrystallizeProceduralMemoryUseCase(
            event_store=event_store,
            skill_repo=skill_repo,
            ledger_audit=ledger_audit
        )

    async def handle_task(self, payload: str) -> str:
        print(f"[L2-Brain Orchestrator] Procesando tarea: {payload}")

        # 1. Recuperar el estado actual de la memoria (Merkle-DAG head)
        last_hash = self.event_store.get_last_leaf_hash()
        last_node = self.event_store.get_by_hash(last_hash) if last_hash != "GENESIS" else None
        
        # Sincronización de Tiempo Lógico (Lamport Ticks)
        current_tick = (last_node.context.lamport_t + 1) if last_node else 1

        # 2. Extracción de intención de fabricación
        intent = AgentIntent(
            intent_type=FabricationIntent.DELETE_FILE if "VETO" in payload else FabricationIntent.READ_FILE,
            target="/",
            rationale=f"Acción gatillada por payload: {payload[:50]}...",
            risk_score=0.9 if "VETO" in payload else 0.1
        )

        # 3. Construcción del Vector 6D (Spec 12)
        context = SixDimensionalContext(
            locus_x="sw.plant.orchestrator",
            locus_y="task.execution",
            locus_z="entity.atomic",
            lamport_t=current_tick,
            authority_a=AuthorityLevel.AGENT,
            intent_i=ContextIntent.MUTATION if "VETO" in payload else ContextIntent.OBSERVATION
        )

        # 4. Auditar intención con el Escudo (L3)
        audit_result = self.shield_port.audit_intent(intent.model_dump_json())
        is_authorized = audit_result.get("authorized", False)

        # 5. Generar Nodo de Memoria 4D-TES (Encadenamiento Causal)
        payload_data = {
            "intent": intent.model_dump(),
            "audit": audit_result
        }
        memory_node = MemoryNode4DTES.generate(
            parent_hash=last_hash,
            context=context,
            payload=json.dumps(payload_data).encode('utf-8')
        )

        # 6. Persistencia Causal (DIP)
        self.event_store.append(memory_node)
        print(f"[L2-Brain Orchestrator] Nodo 4D-TES encadenado: {memory_node.causal_hash} (parent: {last_hash})")

        # 7. Registro de Decisión (Spec 34)
        decision = DecisionRecord(
            decision_id=f"dec_{memory_node.causal_hash[:8]}",
            rationale=intent.rationale,
            impact_blast_radius="local.component",
            context=context,
            target_causal_hash=memory_node.causal_hash,
            witness_hash=audit_result.get("witness_hash", "PENDING_L3_SIGNATURE"),
            timestamp=datetime.utcnow()
        )
        self.ledger_audit.record_decision(decision)

        # 8. Protocolo de Cristalización (Spec 38)
        # Se activa si la certeza del locus es suficiente (Gatillado por evento)
        try:
            certainty = self.ledger_audit.get_certainty_for_locus(context.locus_x)
            if certainty.certainty_score > 0.9 and current_tick % 5 == 0: # Ejemplo: Cada 5 eventos si hay certeza
                print(f"[L2-Brain Orchestrator] Iniciando Cristalización Cognitiva (Certeza: {certainty.certainty_score})")
                chain = self.event_store.get_causal_chain(memory_node.causal_hash, depth=5)
                self.crystallizer.execute(context, chain)
        except Exception as e:
            print(f"[L2-Brain Orchestrator] Cristalización omitida: {e}")

        if not is_authorized:
            print(f"[L2-Brain Orchestrator] !!! VETO DEL ESCUDO (L3) !!! Motivo: {audit_result.get('shield_note')}")
            return "VETO_L3_SECURITY_VIOLATION"

        return "INTENT_QUEUED_L2_VALIDATED"



