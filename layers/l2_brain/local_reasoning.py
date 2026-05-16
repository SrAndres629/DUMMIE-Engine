from __future__ import annotations
import os
import logging
from typing import Any, Dict, List, Optional

from layers.l2_brain.domain.reasoning_logic import ReasoningLogic
from layers.l2_brain.infrastructure.reasoning.providers import (
    ReasoningResult,
    LocalReasoningProvider,
    DeterministicReasoningProvider,
    OllamaGemmaProvider,
    OpenAICompatibleProvider,
    CascadingReasoningProvider
)

logger = logging.getLogger("brain.local_reasoning")

def build_local_reasoning_provider() -> LocalReasoningProvider:
    configured = os.getenv("DUMMIE_LOCAL_REASONING_PROVIDER", "auto").strip().lower()
    deterministic = DeterministicReasoningProvider(ReasoningLogic)
    
    if configured == "deterministic":
        return deterministic
    
    providers: List[LocalReasoningProvider] = []
    if configured in {"ollama", "auto"}:
        providers.append(OllamaGemmaProvider())
    if configured in {"openai", "openai_compatible", "auto"}:
        providers.append(OpenAICompatibleProvider())
    
    providers.append(deterministic)
    return CascadingReasoningProvider(providers)

class LocalReasoningService:
    """
    [L2_BRAIN] Servicio de Razonamiento Local.
    Orquesta llamadas a proveedores (Ollama/OpenAI) con fallback determinista.
    """
    def __init__(self, provider: LocalReasoningProvider | None = None, ledger: Any = None):
        self.provider = provider or build_local_reasoning_provider()
        self.ledger = ledger

    def reasoned_rerank(self, goal: str, candidates: List[Dict[str, Any]], max_selected: int = 5, mode: str = "shadow") -> Dict[str, Any]:
        payload = {"goal": goal, "candidates": candidates, "max_selected": max_selected, "mode": mode}
        result = self.provider.complete_json("reasoned_rerank", payload)
        
        self._record(result, "utility_rerank")
        
        ranked = result.data.get("ranked") if isinstance(result.data, dict) else None
        if not isinstance(ranked, list):
            ranked = ReasoningLogic.rank_candidates(goal, candidates, max_selected)
            
        return {
            "provider": result.provider,
            "provider_status": result.status,
            "latency_ms": result.latency_ms,
            "mode": mode,
            "ranked": ranked,
            "error": result.error,
        }

    def context_shaper(self, goal: str, ranked: List[Dict[str, Any]], token_budget: int = 4000, cloud_agent: str = "generic") -> Dict[str, Any]:
        payload = {"goal": goal, "ranked": ranked, "token_budget": token_budget, "cloud_agent": cloud_agent}
        result = self.provider.complete_json("context_shaper", payload)
        
        self._record(result, "utility_shaper")
        
        packet = result.data if isinstance(result.data, dict) and result.data else ReasoningLogic.shape_context_packet(goal, ranked, token_budget, cloud_agent)
        packet.update({"provider": result.provider, "provider_status": result.status, "latency_ms": result.latency_ms})
        return packet

    def _record(self, result: ReasoningResult, concept: str):
        if not self.ledger or result.status != "ok":
            return
        try:
            self.ledger.record_usage(
                model_id=f"{result.provider}_local",
                tier="local_fast", # Typically local reasoning is fast tier
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                cached_tokens=result.cached_tokens,
                concept=concept,
                source="local_reasoning_service"
            )
        except Exception as e:
            logger.warning(f"Failed to record local reasoning usage: {e}")
