import uuid
import hashlib
from brain.domain.context.models import SixDimensionalContext
from brain.domain.governance.models import LessonRecord, AmbiguityRecord
from brain.domain.memory.ports import ILedgerAuditPort

class CrystallizeLessonsUseCase:
    """
    Caso de Uso: Cristalización de Lecciones y Ambigüedades (Spec 48).
    Automatiza la captura de conocimiento tras fallos o descubrimientos.
    """
    def __init__(self, ledger_audit: ILedgerAuditPort):
        self.ledger_audit = ledger_audit

    def execute_error(
        self,
        context: SixDimensionalContext,
        error: Exception,
        tick: int,
        correction: str = None,
        prevention: str = None
    ):
        """Captura un fallo de ejecución como una lección aprendida."""
        lesson = LessonRecord(
            lesson_id=f"LES-{uuid.uuid4().hex[:8]}",
            tick=tick,
            issue=str(error),
            correction=correction or "Pending manual analysis",
            prevention=prevention or "Enhance SDD validation at L2 boundary",
            context=context
        )
        self.ledger_audit.record_lesson(lesson)
        
        # Degradamos ligeramente la certeza de la capa por el fallo (Spec 42)
        stats = self.ledger_audit.get_certainty_for_locus(context.locus_x)
        self.ledger_audit.update_ontological_map(context.locus_x, {
            "certainty": max(0.0, stats.certainty_score - 0.05),
            "tests": stats.tests_passing,
            "mutations": stats.unverified_mutations + 1
        })

    def execute_ambiguity(self, context: SixDimensionalContext, ambiguity: str, plan: str):
        """Registra una ambigüedad descubierta durante la fabricación."""
        # Hash único basado en contenido real + timestamp para evitar colisiones de ID
        content_hash = hashlib.sha256(
            f"{ambiguity}|{plan}|{uuid.uuid4().hex}".encode()
        ).hexdigest()[:8]
        
        # Estimación de impacto basada en señales del contenido
        impact = "HIGH" if any(kw in ambiguity.lower() for kw in [
            "critical", "security", "data loss", "crash", "corruption",
            "crítico", "seguridad", "pérdida", "corrupción"
        ]) else "MEDIUM"
        
        record = AmbiguityRecord(
            ambiguity_id=f"AMB-{content_hash}",
            context=ambiguity,
            resolution_plan=plan,
            impact_level=impact
        )
        self.ledger_audit.record_ambiguity(record)

