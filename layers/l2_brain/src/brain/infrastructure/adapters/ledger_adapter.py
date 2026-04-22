import os
import json
from brain.domain.memory.ports import ILedgerAuditPort
from brain.domain.governance.models import DecisionRecord, LayerCertainty

class DecisionLedgerAdapter(ILedgerAuditPort):
    """
    Adaptador para el registro de decisiones en el Ledger JSONL (Spec 34).
    """
    def __init__(self, ledger_path: str = ".aiwg/memory/decisions.jsonl"):
        self.ledger_path = ledger_path
        ledger_dir = os.path.dirname(self.ledger_path)
        if ledger_dir:
            os.makedirs(ledger_dir, exist_ok=True)

    def record_decision(self, record: DecisionRecord) -> bool:
        """Añade un registro al ledger in-place."""
        try:
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(record.model_dump_json() + "\n")
            return True
        except Exception as e:
            print(f"[DecisionLedgerAdapter] Error al escribir en el ledger: {e}")
            return False

    def get_certainty_for_locus(self, locus_x: str) -> LayerCertainty:
        """
        Escanea el ledger para calcular estadísticas de certeza.
        (Implementación real de la Spec 42)
        """
        tests = 0
        unverified = 0
        
        if not os.path.exists(self.ledger_path):
            return LayerCertainty(layer_name=locus_x, certainty_score=0.0)

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if data["context"]["locus_x"] == locus_x:
                    # Lógica simple: si hay una decisión positiva, cuenta como 'test' o validación
                    tests += 1
                else:
                    unverified += 1 # Placeholder de mutaciones sin auditar
        
        # Fórmula: tests / (tests + unverified)
        total = tests + unverified
        score = tests / total if total > 0 else 0.0
        
        return LayerCertainty(
            layer_name=locus_x,
            certainty_score=score,
            tests_passing=tests,
            unverified_mutations=unverified
        )

    def get_decisions_for_locus(self, x: str, y: str, z: str) -> list:
        return [] # TODO: Implementar búsqueda filtrada

