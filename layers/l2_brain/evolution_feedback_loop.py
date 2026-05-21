# Spec Reference: 14_value_engineering_and_governance
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("brain.evolution_feedback_loop")


@dataclass
class PerformanceSnapshot:
    session_id: str
    token_usage: int
    latency_ms: float
    success_rate: float
    optimization_level: float
    timestamp: float = time.time()


class EvolutionFeedbackLoop:
    """
    [L2_BRAIN] Motor de Retroalimentación Evolutiva.
    Analiza resultados de ejecuciones previas para optimizar la toma de decisiones futura.
    Implementa el principio de "Bola de Nieve" (Snowball Effect).
    """

    def __init__(self, repository: Any, local_reasoning: Any):
        self.repository = repository  # KuzuRepository
        self.local_reasoning = local_reasoning  # LocalReasoningService
        self.snapshots: List[PerformanceSnapshot] = []

    async def ingest_trace(self, trace_data: Dict[str, Any]):
        """
        Ingiere una traza de Phoenix/Observabilidad y extrae métricas de rendimiento.
        """
        session_id = trace_data.get("session_id", "unknown")
        token_usage = int(trace_data.get("total_tokens", 0))
        latency = float(trace_data.get("latency_ms", 0.0))
        # El éxito se determina por la ausencia de errores críticos en la traza
        success = 1.0 if not trace_data.get("errors") else 0.0

        # [WAVE 10] Cuantización de nivel de optimización
        opt_level = float(trace_data.get("context_reduction_ratio", 0.0))

        snapshot = PerformanceSnapshot(
            session_id=session_id,
            token_usage=token_usage,
            latency_ms=latency,
            success_rate=success,
            optimization_level=opt_level,
        )
        self.snapshots.append(snapshot)
        logger.info(
            f"Feedback Loop: Snapshot ingested for session {session_id}. Success: {success}"
        )

        if success > 0.8:
            await self._crystallize_success_pattern(trace_data)
        else:
            await self._analyze_efficiency_bottleneck(snapshot)

    async def _crystallize_success_pattern(self, trace_data: Dict[str, Any]):
        """
        Guarda un patrón de éxito en el 4D-TES como un "Golden Path".
        """
        try:
            from layers.l2_brain.models import MemoryNode4D

            # Crear un nodo de memoria que represente esta estrategia exitosa
            node = MemoryNode4D.from_intent_context(
                parent_hash=self.repository.get_last_leaf_hash(),
                locus_x="evolution.feedback",
                locus_y="SUCCESS_PATTERN",
                locus_z="GOLDEN_PATH",
                lamport_t=int(time.time()),
                authority_a="FEEDBACK_LOOP",
                intent_i="OPTIMIZATION",
                payload=f"Successful strategy for mission: {trace_data.get('mission_id')}. "
                f"Tokens: {trace_data.get('total_tokens')}. "
                f"OptLevel: {trace_data.get('context_reduction_ratio')}",
            )
            self.repository.create_memory_node(node)
            logger.info(f"Crystallized success pattern: {node.causal_hash}")
        except Exception as e:
            logger.error(f"Failed to crystallize success pattern: {e}")

    async def _analyze_efficiency_bottleneck(self, snapshot: PerformanceSnapshot):
        """
        Analiza por qué una ejecución fue ineficiente o fallida.
        """
        logger.warning(f"Analyzing bottleneck for session {snapshot.session_id}")
        # Aquí se dispararía una misión de auto-corrección vía CognitiveAutoEvolver
        pass


class OptimizationAdvisor:
    """
    Socio estratégico de Capa 2 para la optimización de recursos.
    """

    def __init__(self, feedback_loop: EvolutionFeedbackLoop):
        self.feedback_loop = feedback_loop
        self.current_budget = 4000  # Tokens por defecto

    def recommend_parameters(self, mission_goal: str) -> Dict[str, Any]:
        """
        Recomienda parámetros de optimización basados en el historial de éxito.
        """
        # Simulación de recuperación de Golden Paths desde 4D-TES
        # En una versión avanzada, buscaría nodos similares en Kuzu

        # Lógica heurística inicial
        if "test" in mission_goal.lower() or "debug" in mission_goal.lower():
            return {
                "token_budget": 2000,
                "compression_ratio": 0.8,
                "use_local_cot": True,
            }

        return {
            "token_budget": self.current_budget,
            "compression_ratio": 0.5,
            "use_local_cot": False,
        }
