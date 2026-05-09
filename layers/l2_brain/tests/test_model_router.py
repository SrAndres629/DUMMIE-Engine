"""Tests for model_router and prompt_preprocessor — Phase 1 validation."""
import os
import sys
import pytest

# Ensure l2_brain is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_router import (
    ModelTier,
    TaskComplexity,
    ModelConfig,
    ModelRegistry,
    ModelRouter,
    RoutingDecision,
    build_model_registry,
    classify_task_complexity,
)
from prompt_preprocessor import (
    PromptPreprocessor,
    PreprocessingResult,
    preprocess_deterministic,
)


# ─── Task Difficulty Classifier ───

class TestTaskDifficultyClassifier:

    def test_trivial_formatting(self):
        assert classify_task_complexity("format this file") == TaskComplexity.TRIVIAL

    def test_trivial_status(self):
        assert classify_task_complexity("show me the status") == TaskComplexity.TRIVIAL

    def test_routine_default(self):
        assert classify_task_complexity("add a new endpoint for users") == TaskComplexity.ROUTINE

    def test_complex_refactor(self):
        assert classify_task_complexity("refactor the daemon pipeline") == TaskComplexity.COMPLEX

    def test_complex_many_files(self):
        assert classify_task_complexity("update config", affected_files=10) == TaskComplexity.COMPLEX

    def test_critical_architecture(self):
        assert classify_task_complexity("redesign the schema for memory nodes") == TaskComplexity.CRITICAL

    def test_critical_cross_layer(self):
        result = classify_task_complexity(
            "update the protocol",
            affected_layers=["l0", "l1", "l2"],
        )
        assert result == TaskComplexity.CRITICAL

    def test_critical_security(self):
        assert classify_task_complexity("fix the security vulnerability in auth") == TaskComplexity.CRITICAL

    def test_critical_ontology(self):
        assert classify_task_complexity("refine the ontological map structure") == TaskComplexity.CRITICAL


# ─── Model Registry ───

class TestModelRegistry:

    def test_build_registry_has_local_tiers(self):
        registry = build_model_registry()
        assert registry.get_best(ModelTier.LOCAL_FAST) is not None
        assert registry.get_best(ModelTier.LOCAL_DEEP) is not None

    def test_fallback_when_cloud_unavailable(self):
        registry = ModelRegistry()
        registry.models[ModelTier.LOCAL_DEEP] = [
            ModelConfig("gemma4", ModelTier.LOCAL_DEEP, "ollama")
        ]
        # Cloud STD not configured → should fall back to LOCAL_DEEP
        fallback = registry.get_fallback(ModelTier.CLOUD_STD)
        assert fallback is not None
        assert fallback.tier == ModelTier.LOCAL_DEEP

    def test_no_fallback_returns_none(self):
        registry = ModelRegistry()
        assert registry.get_fallback(ModelTier.LOCAL_FAST) is None


# ─── Model Router ───

class TestModelRouter:

    def test_trivial_routes_to_local_fast(self):
        router = ModelRouter()
        decision = router.route("format this file")
        assert decision.tier == ModelTier.LOCAL_FAST
        assert decision.complexity == TaskComplexity.TRIVIAL
        assert decision.model_id != "none"

    def test_routine_routes_to_local_deep(self):
        router = ModelRouter()
        decision = router.route("add a new config field")
        assert decision.tier == ModelTier.LOCAL_DEEP
        assert decision.complexity == TaskComplexity.ROUTINE

    def test_complex_falls_back_when_no_cloud(self):
        router = ModelRouter()
        decision = router.route("refactor the entire transaction pipeline")
        # Without cloud configured, should fall back
        assert decision.tier in {ModelTier.LOCAL_DEEP, ModelTier.CLOUD_STD}

    def test_force_tier_overrides_classification(self):
        router = ModelRouter()
        decision = router.route("format this", force_tier=ModelTier.LOCAL_DEEP)
        assert decision.tier == ModelTier.LOCAL_DEEP

    def test_budget_enforcement(self):
        registry = build_model_registry()
        # Simulate cloud config
        registry.models[ModelTier.CLOUD_STD] = [
            ModelConfig("flash", ModelTier.CLOUD_STD, "openai_compat", base_url="http://fake")
        ]
        router = ModelRouter(registry)
        router._daily_budget = 100  # Very low budget
        router._total_cloud_tokens = 99  # Almost exhausted

        decision = router.route("refactor the transaction pipeline")
        # Should fall back to local due to budget
        assert decision.tier in {ModelTier.LOCAL_DEEP, ModelTier.LOCAL_FAST}

    def test_record_usage(self):
        router = ModelRouter()
        router.record_usage(1000, ModelTier.CLOUD_STD)
        assert router.budget_remaining == router._daily_budget - 1000

    def test_local_usage_not_counted(self):
        router = ModelRouter()
        initial = router.budget_remaining
        router.record_usage(5000, ModelTier.LOCAL_FAST)
        assert router.budget_remaining == initial  # Unchanged


# ─── Prompt Preprocessor ───

class TestPromptPreprocessor:

    def test_deterministic_detects_create_intent(self):
        result = preprocess_deterministic("create a new model router module")
        assert result.extracted_intent == "CREATE"
        assert len(result.injected_suborders) > 0
        assert "l2" in result.context_refs  # "model" matches l2

    def test_deterministic_detects_fix_intent(self):
        result = preprocess_deterministic("fix the bug in the daemon process")
        assert result.extracted_intent == "FIX"

    def test_deterministic_detects_spanish(self):
        result = preprocess_deterministic("quiero que arregles el problema donde se pierden los datos")
        assert result.detected_language == "es"

    def test_deterministic_detects_layer_refs(self):
        result = preprocess_deterministic("update mcp_server.py and the shield auditor")
        assert "l1" in result.context_refs
        assert "l3" in result.context_refs

    def test_enriched_prompt_contains_original(self):
        original = "add a new endpoint"
        result = preprocess_deterministic(original)
        assert original in result.enriched_prompt

    def test_cross_layer_hint(self):
        result = preprocess_deterministic(
            "update the overseer, nervous system, and brain daemon"
        )
        assert result.complexity_hint == "cross_layer"

    def test_preprocessor_service_deterministic_mode(self):
        preprocessor = PromptPreprocessor(use_llm=False)
        result = preprocessor.process("refactor the skill binder")
        assert isinstance(result, PreprocessingResult)
        assert result.provider == "deterministic"
        assert result.extracted_intent == "REFACTOR"

    def test_suborders_injected_for_delete(self):
        result = preprocess_deterministic("delete the deprecated legacy module")
        assert result.extracted_intent == "DELETE"
        assert any("safe deletion" in s.lower() or "trash" in s.lower() for s in result.injected_suborders)


# ─── Integration: Router + Preprocessor ───

class TestIntegration:

    def test_full_pipeline(self):
        """Simulate: user prompt → preprocess → route → decision."""
        preprocessor = PromptPreprocessor(use_llm=False)
        router = ModelRouter()

        raw_prompt = "necesito refactorizar el daemon para que use el nuevo model router"
        
        # Step 1: Preprocess
        preprocessed = preprocessor.process(raw_prompt)
        assert preprocessed.detected_language == "es"
        assert preprocessed.extracted_intent == "REFACTOR"
        assert "l2" in preprocessed.context_refs

        # Step 2: Route
        decision = router.route(
            preprocessed.enriched_prompt,
            affected_layers=preprocessed.context_refs,
        )
        assert decision.complexity in {TaskComplexity.COMPLEX, TaskComplexity.CRITICAL}
        assert decision.model_id != "none"
