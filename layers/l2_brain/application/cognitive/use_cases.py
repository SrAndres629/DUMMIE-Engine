try:
    from layers.l2_brain.domain.cognitive.models import CognitiveProfile, OptimizationAction
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
    def __init__(self, discovery_port):
        self.discovery_port = discovery_port
        
    def get_relevant_tools(self, objective: str) -> list:
        return self.discovery_port.discover(objective)
