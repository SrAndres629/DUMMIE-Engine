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

    def execute_error(self, context: SixDimensionalContext, error: Exception, tick: int):
        """Captura un fallo de ejecución como una lección aprendida."""
        lesson = LessonRecord(
            lesson_id=f"LES-ERR-{tick}",
            tick=tick,
            issue=str(error),
            correction="Identified via autonomous crystallization",
            prevention="Enhance SDD validation at L2 boundary",
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
        record = AmbiguityRecord(
            ambiguity_id=f"AMB-{context.compute_context_hash()[:8]}",
            context=ambiguity,
            resolution_plan=plan,
            impact_level="MEDIUM"
        )
        self.ledger_audit.record_ambiguity(record)
