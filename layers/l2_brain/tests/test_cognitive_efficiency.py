import pytest
from unittest.mock import MagicMock

try:
    from layers.l2_brain.domain.cognitive.models import CognitiveProfile, OptimizationAction
    from layers.l2_brain.application.cognitive.use_cases import ContextOptimizer, SemanticCapabilityRouter
    from layers.l2_brain.infrastructure.cognitive.adapters import KuzuCompressionAdapter, KuzuQuantizationAdapter, MCPGatewayAdapter
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from domain.cognitive.models import CognitiveProfile, OptimizationAction
    from application.cognitive.use_cases import ContextOptimizer, SemanticCapabilityRouter
    from infrastructure.cognitive.adapters import KuzuCompressionAdapter, KuzuQuantizationAdapter, MCPGatewayAdapter

def test_hexagonal_flow():
    profile = CognitiveProfile(hard_limit=100, soft_threshold=50)
    compressor = KuzuCompressionAdapter()
    quantizer = KuzuQuantizationAdapter()
    
    optimizer = ContextOptimizer(profile, compressor, quantizer)
    
    # 1. Probar compresión (umbral > 50 tokens)
    context = "a " * 150 # 300 chars -> ~75 tokens
    new_context = optimizer.optimize(context)
    assert len(new_context) < len(context)
    
    # 2. Probar cuantización (umbral > 100 tokens)
    context_large = "a " * 300 # 600 chars -> ~150 tokens
    new_context_large = optimizer.optimize(context_large)
    assert len(new_context_large) < len(context_large)
