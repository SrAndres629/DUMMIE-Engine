# Spec Reference: 12_6d_context_model
try:
    from layers.l2_brain.domain.cognitive.models import (
        CognitiveProfile,
        OptimizationAction,
    )
except ImportError:
    import sys
    import os

    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    from domain.cognitive.models import CognitiveProfile, OptimizationAction


class ContextOptimizer:
    def __init__(self, profile: CognitiveProfile, compression_port, quantization_port):
        self.profile = profile
        self.compression_port = compression_port
        self.quantization_port = quantization_port

    def optimize(self, current_context: str) -> str:
        estimated_tokens = len(current_context) // 4
        action = self.profile.evaluate(estimated_tokens)

        if action == OptimizationAction.COMPRESS:
            return self.compression_port.compress(current_context)
        elif action == OptimizationAction.QUANTIZE:
            return self.quantization_port.quantize(current_context)

        return current_context


class SemanticCapabilityRouter:
    def __init__(self, discovery_port, event_bus=None):
        self.discovery_port = discovery_port
        self.event_bus = event_bus

    async def get_relevant_tools(self, objective: str) -> list:
        import time
        start = time.perf_counter()
        
        tools = self.discovery_port.discover(objective)
        
        if self.event_bus:
            # Emitir métricas de ruteo
            await self.event_bus.publish("ToolSelection", {
                "query": objective,
                "selected_tool": tools[0]["id"] if tools else "none",
                "relevance_score": tools[0].get("score", 0.0) if tools else 0.0,
                "latency_ms": (time.perf_counter() - start) * 1000,
                "timestamp": time.time()
            })
        return tools
