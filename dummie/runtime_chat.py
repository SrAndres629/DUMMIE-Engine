from __future__ import annotations

# Spec: DE-V2-L2-202 Runtime Lifecycle Chat Contract
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from dummie.aiwg import DummieAiwgIntegration
from dummie.paths import AIWG
from dummie.providers import DummieProviderRegistry
from dummie.strategic_partner import DummieStrategicPartner

try:
    from layers.l2_brain.model_router import (
        ModelRouter,
        ModelTier,
        build_model_registry,
    )
except ModuleNotFoundError:
    from layers.l2_brain.model_mesh.model_router import (
        ModelRouter,
        ModelTier,
        build_model_registry,
    )

try:
    from layers.l2_brain.prompt_preprocessor import PromptPreprocessor
except ModuleNotFoundError:
    from layers.l2_brain.application.prompt_preprocessor import PromptPreprocessor

try:
    from layers.l2_brain.token_cost_ledger import TokenCostLedger
except ModuleNotFoundError:
    from layers.l2_brain.model_mesh.token_cost_ledger import TokenCostLedger


DEFAULT_RUNTIME_CHAT_REGISTRY: dict[str, Any] = {
    "schema_version": "dummie.runtime_chat.v1",
    "mode": "runtime_lifecycle_orchestration",
    "preprocessing": {
        "use_llm": False,
    },
    "routing": {
        "enabled": True,
        "force_tier": "",
        "concept": "main",
    },
    "provider_priority": [
        "opencode",
        "codex_cli",
        "gemini_cli",
        "openrouter",
        "groq",
        "deepseek",
        "antigravity",
    ],
}


@dataclass
class RuntimeChatResult:
    decision: str
    goal_type: str
    strategic_questions: list[str]
    tool_opportunities: list[dict[str, Any]]
    roadmap: list[dict[str, Any]]
    preprocessing_provider: str
    routing_tier: str
    routing_model_id: str
    routing_reason: str
    selected_provider: str
    selected_provider_reason: str
    receipt: dict[str, Any]
    raw_data: dict[str, Any]


class DummieRuntimeChat:
    def __init__(
        self,
        aiwg_root: Path = AIWG,
        aiwg: DummieAiwgIntegration | None = None,
        providers: DummieProviderRegistry | None = None,
        partner: DummieStrategicPartner | None = None,
    ):
        self.aiwg_root = Path(aiwg_root)
        self.aiwg = aiwg or DummieAiwgIntegration()
        self.providers = providers or DummieProviderRegistry()
        self.partner = partner or DummieStrategicPartner()
        self.registry_path = self.aiwg_root / "runtime" / "runtime_chat_registry.yaml"

    def run(
        self, prompt: str, low_cost: bool = False, session_id: str = "CURRENT"
    ) -> RuntimeChatResult:
        registry = self._load_registry()
        preprocessing = registry.get("preprocessing", {})
        routing_cfg = registry.get("routing", {})
        provider_priority = registry.get("provider_priority", [])

        use_llm = bool(preprocessing.get("use_llm", False)) and not low_cost
        preprocessor = PromptPreprocessor(use_llm=use_llm)
        pre = preprocessor.process(prompt)

        token_ledger = TokenCostLedger(root=self.aiwg_root)
        router = ModelRouter(registry=build_model_registry(), ledger=token_ledger)
        force_tier = _parse_force_tier(routing_cfg.get("force_tier", ""))
        decision = router.route(
            pre.enriched_prompt,
            affected_layers=pre.context_refs,
            force_tier=force_tier,
            hook_metadata=pre.hook_metadata,
            session_id=session_id,
            concept=str(routing_cfg.get("concept", "main")),
        )

        lifecycle = self.partner.advise(pre.enriched_prompt)
        providers_status = self.providers.get_providers_status(live_check=True)
        selected_provider, selected_reason = _pick_provider(
            model_id=decision.model_id,
            tier=decision.tier.value,
            providers_status=providers_status,
            provider_priority=provider_priority
            if isinstance(provider_priority, list)
            else [],
        )

        payload = {
            "decision": "PASS",
            "mode": registry.get("mode", DEFAULT_RUNTIME_CHAT_REGISTRY["mode"]),
            "query": prompt,
            "runtime_registry": registry,
            "preprocessing": {
                "provider": pre.provider,
                "intent": pre.extracted_intent,
                "language": pre.detected_language,
                "complexity_hint": pre.complexity_hint,
                "context_refs": pre.context_refs,
                "latency_ms": pre.latency_ms,
                "error": pre.error,
            },
            "routing": {
                "tier": decision.tier.value,
                "complexity": decision.complexity.value,
                "model_id": decision.model_id,
                "reason": decision.reason,
                "estimated_tokens": decision.estimated_tokens,
                "latency_ms": decision.latency_ms,
                "hook_metadata": decision.hook_metadata,
            },
            "provider_selection": {
                "selected_provider": selected_provider,
                "reason": selected_reason,
                "provider_status": providers_status.get(selected_provider, {}),
            },
            "lifecycle": lifecycle,
        }

        report_path = self.aiwg.write_report("runtime_chat_latest.json", payload)
        trace_payload = {
            "decision": "PASS",
            "query": prompt,
            "evidence_refs": [
                str(report_path.relative_to(self.aiwg_root.parent)),
                ".aiwg/reports/provider_status_latest.json",
            ],
            "routing_tier": decision.tier.value,
            "routing_model_id": decision.model_id,
            "selected_provider": selected_provider,
        }
        self.aiwg.write_report("runtime_chat_trace_latest.json", trace_payload)
        receipt = self.aiwg.write_receipt(
            "runtime-chat",
            "PASS",
            {
                "query": prompt,
                "routing_tier": decision.tier.value,
                "routing_model_id": decision.model_id,
                "selected_provider": selected_provider,
            },
        )

        lifecycle_questions = lifecycle.get("strategic_questions", [])
        lifecycle_tools = lifecycle.get("tool_opportunities", [])
        lifecycle_roadmap = lifecycle.get("roadmap", [])
        goal_type = lifecycle.get("goal_classification", {}).get("goal_type", "unknown")

        return RuntimeChatResult(
            decision="PASS",
            goal_type=goal_type,
            strategic_questions=lifecycle_questions
            if isinstance(lifecycle_questions, list)
            else [],
            tool_opportunities=lifecycle_tools
            if isinstance(lifecycle_tools, list)
            else [],
            roadmap=lifecycle_roadmap if isinstance(lifecycle_roadmap, list) else [],
            preprocessing_provider=pre.provider,
            routing_tier=decision.tier.value,
            routing_model_id=decision.model_id,
            routing_reason=decision.reason,
            selected_provider=selected_provider,
            selected_provider_reason=selected_reason,
            receipt=receipt,
            raw_data=payload,
        )

    def _load_registry(self) -> dict[str, Any]:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self.registry_path.write_text(
                yaml.safe_dump(DEFAULT_RUNTIME_CHAT_REGISTRY, sort_keys=False),
                encoding="utf-8",
            )
            return dict(DEFAULT_RUNTIME_CHAT_REGISTRY)

        try:
            loaded = (
                yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
            )
        except Exception:
            return dict(DEFAULT_RUNTIME_CHAT_REGISTRY)
        if not isinstance(loaded, dict):
            return dict(DEFAULT_RUNTIME_CHAT_REGISTRY)
        merged = dict(DEFAULT_RUNTIME_CHAT_REGISTRY)
        merged.update(loaded)
        return merged


def _parse_force_tier(raw: Any) -> ModelTier | None:
    val = str(raw or "").strip().lower()
    if not val:
        return None
    for tier in ModelTier:
        if tier.value == val:
            return tier
    return None


def _pick_provider(
    model_id: str,
    tier: str,
    providers_status: dict[str, dict[str, Any]],
    provider_priority: list[str],
) -> tuple[str, str]:
    if "/" in model_id:
        prefix = model_id.split("/", 1)[0].strip()
        if prefix in providers_status:
            return prefix, "model_prefix"

    if tier in {"local_fast", "local_deep"}:
        return "ollama", "local_tier_default"

    for provider_id in provider_priority:
        status = providers_status.get(provider_id, {})
        if not status:
            continue
        if status.get("auth_status") == "ready":
            return provider_id, "priority_ready_provider"

    for provider_id in provider_priority:
        if provider_id in providers_status:
            return provider_id, "priority_fallback"

    return "unknown", "no_provider_match"
