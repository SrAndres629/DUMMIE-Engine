"""
[L2_BRAIN] Model Router — Intelligent Model Tier Assignment.

Routes each task to the optimal model tier based on difficulty classification,
token budget, and operational context. Designed to minimize cloud token consumption
by delegating ~65% of work to local models.

Spec: DE-PHASE1-ROUTER
"""
from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, Optional

logger = logging.getLogger("model-router")


# ─────────────────────────────────────────────
# Schema: Model Tiers
# ─────────────────────────────────────────────

class ModelTier(str, Enum):
    """
    Four-tier model hierarchy optimizing for cost/capability.

    LOCAL_FAST:  ~2-4b params. Classification, parsing, monitoring. 0 cloud tokens.
    LOCAL_DEEP:  ~12-30b params. Reasoning, rewriting, validation. 0 cloud tokens.
    CLOUD_STD:   Cloud flash models. Normal operations, coding, integration.
    CLOUD_PREM:  Top-tier cloud models. Architecture, critical decisions.
    """
    LOCAL_FAST = "local_fast"
    LOCAL_DEEP = "local_deep"
    CLOUD_STD = "cloud_std"
    CLOUD_PREM = "cloud_prem"


class TaskComplexity(str, Enum):
    """Complexity classification output from the difficulty classifier."""
    TRIVIAL = "trivial"       # Formatting, parsing, simple queries
    ROUTINE = "routine"       # Standard coding, config changes
    COMPLEX = "complex"       # Multi-file refactoring, integration
    CRITICAL = "critical"     # Architecture, security, cross-layer design


# ─────────────────────────────────────────────
# Schema: Routing Decision
# ─────────────────────────────────────────────

@dataclass
class RoutingDecision:
    """Immutable output of the router."""
    tier: ModelTier
    complexity: TaskComplexity
    model_id: str
    reason: str
    estimated_tokens: int = 0
    preprocessing_applied: bool = False
    enriched_prompt: str = ""
    latency_ms: float = 0.0


# ─────────────────────────────────────────────
# Schema: Model Registry
# ─────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Configuration for a specific model in a tier."""
    model_id: str
    tier: ModelTier
    provider: str                  # "ollama", "openai_compat", "cloud_api"
    base_url: str = ""
    api_key_env: str = ""          # env var name, never the key itself
    max_tokens: int = 4096
    timeout_s: float = 30.0
    cost_per_1k_tokens: float = 0.0  # 0 for local models


@dataclass
class ModelRegistry:
    """
    Central registry of available models per tier.
    Populated from environment variables and Ollama inventory.
    """
    models: dict[ModelTier, list[ModelConfig]] = field(default_factory=dict)

    def get_best(self, tier: ModelTier) -> ModelConfig | None:
        """Return first available model for the requested tier."""
        candidates = self.models.get(tier, [])
        return candidates[0] if candidates else None

    def get_fallback(self, tier: ModelTier) -> ModelConfig | None:
        """If requested tier is unavailable, cascade down."""
        cascade = {
            ModelTier.CLOUD_PREM: [ModelTier.CLOUD_STD, ModelTier.LOCAL_DEEP],
            ModelTier.CLOUD_STD: [ModelTier.LOCAL_DEEP, ModelTier.LOCAL_FAST],
            ModelTier.LOCAL_DEEP: [ModelTier.LOCAL_FAST],
            ModelTier.LOCAL_FAST: [],
        }
        for fallback_tier in cascade.get(tier, []):
            model = self.get_best(fallback_tier)
            if model:
                return model
        return None


def build_model_registry() -> ModelRegistry:
    """Build registry from environment and Ollama state."""
    registry = ModelRegistry()

    # Local Fast — small model for classification
    local_fast_model = os.getenv("DUMMIE_LOCAL_FAST_MODEL", "gemma4:e4b")
    local_fast_url = os.getenv("DUMMIE_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    registry.models[ModelTier.LOCAL_FAST] = [
        ModelConfig(
            model_id=local_fast_model,
            tier=ModelTier.LOCAL_FAST,
            provider="ollama",
            base_url=local_fast_url,
            timeout_s=float(os.getenv("DUMMIE_LOCAL_FAST_TIMEOUT", "2.0")),
        )
    ]

    # Local Deep — larger model for reasoning
    local_deep_model = os.getenv("DUMMIE_LOCAL_DEEP_MODEL", "gemma4:e4b")
    registry.models[ModelTier.LOCAL_DEEP] = [
        ModelConfig(
            model_id=local_deep_model,
            tier=ModelTier.LOCAL_DEEP,
            provider="ollama",
            base_url=local_fast_url,
            timeout_s=float(os.getenv("DUMMIE_LOCAL_DEEP_TIMEOUT", "15.0")),
            max_tokens=8192,
        )
    ]

    # Cloud Standard — flash-tier API
    cloud_std_url = os.getenv("DUMMIE_CLOUD_STD_BASE_URL", "")
    if cloud_std_url:
        registry.models[ModelTier.CLOUD_STD] = [
            ModelConfig(
                model_id=os.getenv("DUMMIE_CLOUD_STD_MODEL", "gemini-2.5-flash"),
                tier=ModelTier.CLOUD_STD,
                provider="openai_compat",
                base_url=cloud_std_url,
                api_key_env="DUMMIE_CLOUD_STD_API_KEY",
                cost_per_1k_tokens=0.15,
                timeout_s=30.0,
            )
        ]

    # Cloud Premium — top-tier API
    cloud_prem_url = os.getenv("DUMMIE_CLOUD_PREM_BASE_URL", "")
    if cloud_prem_url:
        registry.models[ModelTier.CLOUD_PREM] = [
            ModelConfig(
                model_id=os.getenv("DUMMIE_CLOUD_PREM_MODEL", "claude-opus-4"),
                tier=ModelTier.CLOUD_PREM,
                provider="openai_compat",
                base_url=cloud_prem_url,
                api_key_env="DUMMIE_CLOUD_PREM_API_KEY",
                cost_per_1k_tokens=15.0,
                timeout_s=60.0,
                max_tokens=16384,
            )
        ]

    return registry


# ─────────────────────────────────────────────
# Task Difficulty Classifier
# ─────────────────────────────────────────────

# Complexity signals extracted from prompt analysis
_CRITICAL_SIGNALS = re.compile(
    r"\b(architect|redesign|migrate|security|cross.?layer|schema.?change|"
    r"breaking.?change|data.?model|protocol|ontolog\w*|merkle|consensus)\b",
    re.IGNORECASE,
)
_COMPLEX_SIGNALS = re.compile(
    r"\b(refactor|multi.?file|integration|pipeline|orchestrat|"
    r"daemon|transaction|saga|workflow|deploy)\b",
    re.IGNORECASE,
)
_TRIVIAL_SIGNALS = re.compile(
    r"\b(format|lint|typo|comment|rename|log|print|status|list|show|version)\b",
    re.IGNORECASE,
)


def classify_task_complexity(
    prompt: str,
    affected_layers: list[str] | None = None,
    affected_files: int = 0,
) -> TaskComplexity:
    """
    Pure function: classify task complexity from prompt text and metadata.
    Uses lexical signals + structural heuristics (no LLM call needed).
    """
    affected_layers = affected_layers or []

    # Check critical signals first
    if _CRITICAL_SIGNALS.search(prompt):
        return TaskComplexity.CRITICAL

    # Multi-layer changes are inherently complex
    if len(affected_layers) > 2:
        return TaskComplexity.CRITICAL

    # Check complex signals
    if _COMPLEX_SIGNALS.search(prompt) or affected_files > 5:
        return TaskComplexity.COMPLEX

    # Check trivial signals
    if _TRIVIAL_SIGNALS.search(prompt) and affected_files <= 1:
        return TaskComplexity.TRIVIAL

    # Default to routine
    return TaskComplexity.ROUTINE


# ─────────────────────────────────────────────
# Complexity → Tier Mapping
# ─────────────────────────────────────────────

_COMPLEXITY_TO_TIER: dict[TaskComplexity, ModelTier] = {
    TaskComplexity.TRIVIAL: ModelTier.LOCAL_FAST,
    TaskComplexity.ROUTINE: ModelTier.LOCAL_DEEP,
    TaskComplexity.COMPLEX: ModelTier.CLOUD_STD,
    TaskComplexity.CRITICAL: ModelTier.CLOUD_PREM,
}


# ─────────────────────────────────────────────
# Model Router (Orchestrator)
# ─────────────────────────────────────────────

class ModelRouter:
    """
    Routes tasks to the optimal model tier.
    Performs difficulty classification, tier selection, and fallback resolution.
    """

    def __init__(self, registry: Optional[Any] = None, ledger: Any = None):
        if registry is None:
            registry = build_model_registry()
        self.registry = registry
        self.ledger = ledger
        self._total_cloud_tokens = 0
        self._daily_budget = int(os.getenv("DUMMIE_DAILY_TOKEN_BUDGET", "500000"))

    def route(
        self,
        prompt: str,
        affected_layers: list[str] | None = None,
        affected_files: int = 0,
        force_tier: ModelTier | None = None,
    ) -> RoutingDecision:
        """
        Determine the optimal model tier and return a RoutingDecision.
        """
        started = time.perf_counter()

        complexity = classify_task_complexity(prompt, affected_layers, affected_files)
        target_tier = force_tier or _COMPLEXITY_TO_TIER[complexity]

        # Resolve model
        model = self.registry.get_best(target_tier)
        if not model:
            model = self.registry.get_fallback(target_tier)
            if model:
                logger.warning(
                    "Tier %s unavailable, falling back to %s (%s)",
                    target_tier.value, model.tier.value, model.model_id,
                )
                target_tier = model.tier

        if not model:
            # Emergency: no models available at all
            logger.error("No models available for any tier. Returning degraded decision.")
            return RoutingDecision(
                tier=ModelTier.LOCAL_FAST,
                complexity=complexity,
                model_id="none",
                reason="no_models_available",
                latency_ms=(time.perf_counter() - started) * 1000,
            )

        # Budget gate for cloud models
        estimated = _estimate_prompt_tokens(prompt)
        if model.tier in {ModelTier.CLOUD_STD, ModelTier.CLOUD_PREM}:
            if self._total_cloud_tokens + estimated > self._daily_budget:
                fallback = self.registry.get_best(ModelTier.LOCAL_DEEP)
                if fallback:
                    logger.warning(
                        "Daily token budget exceeded (%d/%d). Falling back to local.",
                        self._total_cloud_tokens, self._daily_budget,
                    )
                    model = fallback
                    target_tier = ModelTier.LOCAL_DEEP

        reason = (
            f"complexity={complexity.value} → tier={target_tier.value} "
            f"model={model.model_id} est_tokens={estimated}"
        )

        return RoutingDecision(
            tier=target_tier,
            complexity=complexity,
            model_id=model.model_id,
            reason=reason,
            estimated_tokens=estimated,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    def record_usage(self, tokens: int, tier: ModelTier) -> None:
        """Track token usage for budget enforcement."""
        if tier in {ModelTier.CLOUD_STD, ModelTier.CLOUD_PREM}:
            self._total_cloud_tokens += tokens

    @property
    def budget_remaining(self) -> int:
        return max(0, self._daily_budget - self._total_cloud_tokens)


def _estimate_prompt_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token."""
    return max(1, len(text) // 4)
