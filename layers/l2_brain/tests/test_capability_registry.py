# Spec: DE-V2-L2-106
import pytest
from brain.domain.capability_registry import CapabilityRegistry, ModelCapability, ModelExpertise

def test_capability_registry_selection():
    registry = CapabilityRegistry()
    
    # Register a specialist code model
    coding_model = ModelCapability(
        model_id="deepseek-coder-v2",
        expertise=[ModelExpertise.CODING],
        context_window=128000,
        max_output_tokens=4096,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.02,
        provider="ollama",
        is_local=True,
        latency_score=0.2
    )
    
    # Register a reasoning model
    reasoning_model = ModelCapability(
        model_id="claude-3-5-sonnet",
        expertise=[ModelExpertise.REASONING, ModelExpertise.GENERAL],
        context_window=200000,
        max_output_tokens=8192,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.15,
        provider="anthropic",
        is_local=False,
        latency_score=0.6
    )
    
    registry.register_model(coding_model)
    registry.register_model(reasoning_model)
    
    # Test selection
    best_code = registry.get_best_model_for(ModelExpertise.CODING)
    assert best_code.model_id == "deepseek-coder-v2"
    
    best_reasoning = registry.get_best_model_for(ModelExpertise.REASONING)
    assert best_reasoning.model_id == "claude-3-5-sonnet"
    
    # Test fallback
    registry.default_model = "claude-3-5-sonnet"
    best_unknown = registry.get_best_model_for(ModelExpertise.VISION)
    assert best_unknown.model_id == "claude-3-5-sonnet"
