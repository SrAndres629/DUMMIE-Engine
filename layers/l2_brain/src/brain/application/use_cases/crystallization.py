import hashlib
from typing import List
from brain.domain.context.models import SixDimensionalContext
from brain.domain.memory.models import MemoryNode4DTES, CrystallizedSkill
from brain.domain.memory.ports import IEventStorePort, ISkillRepositoryPort, ILedgerAuditPort
from brain.domain.governance.models import DecisionRecord

class CrystallizeProceduralMemoryUseCase:
    """
    Caso de Uso: Cristalización de Memoria Procedimental (Spec 38).
    Orquesta la destilación de experiencias efímeras en habilidades permanentes.
    """
    def __init__(
        self,
        event_store: IEventStorePort,
        skill_repo: ISkillRepositoryPort,
        ledger_audit: ILedgerAuditPort
    ):
        self.event_store = event_store
        self.skill_repo = skill_repo
        self.ledger_audit = ledger_audit

    def execute(self, context: SixDimensionalContext, source_nodes: List[MemoryNode4DTES]) -> CrystallizedSkill:
        """
        Ejecuta el protocolo de cristalización:
        1. Evalúa la Certeza Ontológica de los nodos fuente.
        2. Genera el contrato de la habilidad (YAML).
        3. Persiste la habilidad y registra la decisión causal.
        """
        # [Lógica de L2] Evaluación de Certeza (Spec 42)
        stats = self.ledger_audit.get_certainty_for_locus(context.locus_x)
        
        # Fórmula de Certeza Determinista: Tests / (Tests + Unverified Mutations)
        total_signals = stats.tests_passing + stats.unverified_mutations
        certainty_score = stats.tests_passing / total_signals if total_signals > 0 else 0.0
        
        if certainty_score < 0.85: # Umbral definido en Spec 38
            raise ValueError(f"Certeza insuficiente ({certainty_score:.2f}) para cristalización en {context.locus_x}")

        # [Destilación] Generación de la Skill
        skill_id = f"SKILL-{context.compute_context_hash()[:8]}"
        yaml_payload = f"spec_id: {skill_id}\nstatus: ACTIVE\nintent: CRYSTALLIZATION\norigin_locus: {context.locus_x}"
        
        # Proveniencia Causal (Audit Trace)
        source_hashes = [node.causal_hash for node in source_nodes]
        
        # [Cierre Criptográfico] SHA-256(payload + causal_provenance)
        skill_seed = f"{yaml_payload}{''.join(source_hashes)}".encode('utf-8')
        skill_hash = hashlib.sha256(skill_seed).hexdigest()
        
        skill = CrystallizedSkill(
            skill_id=skill_id,
            yaml_payload=yaml_payload,
            source_causal_hashes=source_hashes,
            skill_hash=skill_hash
        )

        # [Persistencia]
        self.skill_repo.save_skill(skill)
        
        # [Gobernanza] Registro inmutable del aprendizaje
        decision = DecisionRecord(
            decision_id=f"DEC-{skill_id}",
            rationale=f"Cristalización procedimental del locus {context.locus_x} (Certainty: {certainty_score:.2f})",
            impact_blast_radius="domain.procedural",
            context=context,
            target_causal_hash=source_hashes[-1] if source_hashes else "ROOT",
            witness_hash=hashlib.sha256(skill_hash.encode()).hexdigest()[:16] # Firma derivada
        )
        self.ledger_audit.record_decision(decision)

        return skill

