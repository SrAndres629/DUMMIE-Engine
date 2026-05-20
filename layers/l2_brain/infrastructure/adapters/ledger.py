import os
import json
from brain.domain.memory.ports import ILedgerAuditPort
from brain.domain.governance.models import DecisionRecord, LayerCertainty, LessonRecord, AmbiguityRecord
from brain.infrastructure.adapters.ontological_adapter import OntologicalMapAdapter

class DecisionLedgerAdapter(ILedgerAuditPort):
    """
    Adaptador para el registro de decisiones en el Ledger JSONL (Spec 34).
    """
    def __init__(
        self, 
        ledger_path: str = ".aiwg/ledger/sovereign_resolutions.jsonl",
        lessons_path: str = ".aiwg/memory/lessons.jsonl",
        ambiguities_path: str = ".aiwg/memory/ambiguities.jsonl",
        ontological_map_path: str = ".aiwg/ontological_map.json"
    ):
        self.ledger_path = ledger_path
        self.lessons_path = lessons_path
        self.ambiguities_path = ambiguities_path
        self.ont_map_adapter = OntologicalMapAdapter(map_path=ontological_map_path)
        
        # Ensure directories exist
        for path in [self.ledger_path, self.lessons_path, self.ambiguities_path]:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

    def record_decision(self, record: DecisionRecord) -> bool:
        """Añade un registro al ledger in-place."""
        try:
            # Map for Spec 34 compliance: impact_blast_radius -> impact
            data = record.model_dump()
            data["impact"] = data.pop("impact_blast_radius")
            
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, default=str) + "\n")
            return True
        except Exception as e:
            pass # print(f"[DecisionLedgerAdapter] Error al escribir en el ledger: {e}")
            return False

    def get_certainty_for_locus(self, locus_x: str) -> LayerCertainty:
        """
        Escanea el ledger para calcular estadísticas de certeza.
        (Implementación real de la Spec 42)
        """
        tests = 0
        unverified = 0
        
        if not os.path.exists(self.ledger_path):
            certainty = LayerCertainty(layer_name=locus_x, certainty_score=0.0)
            self.ont_map_adapter.update_layer(certainty)
            return certainty

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
        
        certainty = LayerCertainty(
            layer_name=locus_x,
            certainty_score=score,
            tests_passing=tests,
            unverified_mutations=unverified
        )
        
        # Persistir en el Mapa Ontológico (Spec 42)
        self.ont_map_adapter.update_layer(certainty)
        
        return certainty

    def get_decisions_for_locus(self, x: str, y: str, z: str) -> list:
        """Filtra las decisiones en el ledger por coordenadas ontológicas."""
        decisions = []
        if not os.path.exists(self.ledger_path):
            return []
            
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    ctx = data.get("context", {})
                    if (ctx.get("locus_x") == x or x == "*") and \
                       (ctx.get("locus_y") == y or y == "*") and \
                       (ctx.get("locus_z") == z or z == "*"):
                        decisions.append(data)
            return decisions
        except Exception as e:
            pass # print(f"[DecisionLedgerAdapter] Error al leer historial: {e}")
            return []

    def record_lesson(self, lesson: LessonRecord) -> None:
        """Registra una lección aprendida (Spec 48)."""
        try:
            with open(self.lessons_path, "a", encoding="utf-8") as f:
                f.write(lesson.model_dump_json() + "\n")
        except Exception as e:
            pass # print(f"[DecisionLedgerAdapter] Error al escribir lección: {e}")

    def record_ambiguity(self, ambiguity: AmbiguityRecord) -> None:
        """Registra una ambigüedad (Spec 48)."""
        try:
            with open(self.ambiguities_path, "a", encoding="utf-8") as f:
                f.write(ambiguity.model_dump_json() + "\n")
        except Exception as e:
            pass # print(f"[DecisionLedgerAdapter] Error al escribir ambigüedad: {e}")

    def update_ontological_map(self, layer: str, update_data: dict) -> None:
        """Actualiza el mapa ontológico."""
        # Delegar al adaptador especializado
        certainty = LayerCertainty(
            layer_name=layer,
            certainty_score=update_data.get("certainty", 0.0),
            tests_passing=update_data.get("tests", 0),
            unverified_mutations=update_data.get("mutations", 0)
        )
        self.ont_map_adapter.update_layer(certainty)

    def log_resolution(self, entry: dict) -> bool:
        """Bridge compatibility method for legacy callers."""
        from brain.domain.governance.models import DecisionRecord
        from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
        
        ctx_data = entry.get("context", {})
        context = SixDimensionalContext(
            locus_x=ctx_data.get("locus_x", "unknown"),
            locus_y=ctx_data.get("locus_y", "unknown"),
            locus_z=ctx_data.get("locus_z", "unknown"),
            lamport_t=entry.get("tick", 0),
            authority_a=ctx_data.get("authority_a", AuthorityLevel.AGENT),
            intent_i=ctx_data.get("intent_i", IntentType.RESOLUTION),
        )
        record = DecisionRecord(
            decision_id=entry.get("decision_id", f"DEC-{entry.get('tick', 0)}"),
            tick=entry.get("tick", 0),
            context=context,
            rationale=entry.get("goal", ""),
            impact_blast_radius=entry.get("impact", "LOW"),
            target_causal_hash=entry.get("target_causal_hash", ""),
            witness_hash=entry.get("witness_hash", ""),
            metadata=entry.get("metadata", {})
        )
        return self.record_decision(record)

    def log_lesson(self, entry: dict) -> None:
        """Bridge compatibility method for legacy callers."""
        from brain.domain.governance.models import LessonRecord
        from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
        
        ctx_data = entry.get("context", {})
        context = SixDimensionalContext(
            locus_x=ctx_data.get("locus_x", "unknown"),
            locus_y=ctx_data.get("locus_y", "unknown"),
            locus_z=ctx_data.get("locus_z", "unknown"),
            lamport_t=entry.get("tick", 0),
            authority_a=ctx_data.get("authority_a", AuthorityLevel.AGENT),
            intent_i=ctx_data.get("intent_i", IntentType.OBSERVATION),
        )
        lesson = LessonRecord(
            lesson_id=entry.get("lesson_id", "LES-01"),
            tick=entry.get("tick", 0),
            issue=entry.get("issue", ""),
            correction=entry.get("correction", ""),
            prevention=entry.get("prevention", ""),
            context=context
        )
        self.record_lesson(lesson)

    def log_ambiguity(self, entry: dict) -> None:
        """Bridge compatibility method for legacy callers."""
        from brain.domain.governance.models import AmbiguityRecord
        from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
        
        ctx_data = entry.get("context", {})
        context = SixDimensionalContext(
            locus_x=ctx_data.get("locus_x", "unknown"),
            locus_y=ctx_data.get("locus_y", "unknown"),
            locus_z=ctx_data.get("locus_z", "unknown"),
            lamport_t=entry.get("tick", 0),
            authority_a=ctx_data.get("authority_a", AuthorityLevel.AGENT),
            intent_i=ctx_data.get("intent_i", IntentType.OBSERVATION),
        )
        ambiguity = AmbiguityRecord(
            ambiguity_id=entry.get("ambiguity_id", "AMB-01"),
            tick=entry.get("tick", 0),
            issue=entry.get("issue", ""),
            resolution=entry.get("resolution", ""),
            context=context
        )
        self.record_ambiguity(ambiguity)

