"""
[L2_BRAIN] Prompt Preprocessor — Local Semantic Refinement Pipeline.

Pipeline: raw_prompt → semantic_parse → intent_extract → context_inject → enriched_prompt

All preprocessing runs on LOCAL models (0 cloud tokens). The enriched prompt
is then sent to the cloud model with sub-orders implanted for precise execution.

Spec: DE-PHASE1-PREPROCESSOR
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any
from urllib import request as urlrequest
from urllib.error import URLError

logger = logging.getLogger("prompt-preprocessor")


@dataclass
class PreprocessingResult:
    """Output of the preprocessing pipeline."""
    original_prompt: str
    enriched_prompt: str
    extracted_intent: str
    detected_language: str
    complexity_hint: str
    injected_suborders: list[str] = field(default_factory=list)
    context_refs: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    provider: str = "deterministic"
    error: str = ""
    hook_metadata: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────
# Deterministic Preprocessing (Zero-LLM fallback)
# ─────────────────────────────────────────────

_INTENT_PATTERNS = {
    "CREATE": re.compile(r"\b(crea|create|new|genera|build|implement|add)\b", re.IGNORECASE),
    "FIX": re.compile(r"\b(fix|repair|corrige|arregla|debug|solve|resolve)\b", re.IGNORECASE),
    "REFACTOR": re.compile(r"\b(refactor\w*|reorgan|restructur|clean|simplif|optimiz)\b", re.IGNORECASE),
    "ANALYZE": re.compile(r"\b(analy|audit|review|inspect|evalua|diagnos|investig)\b", re.IGNORECASE),
    "DELETE": re.compile(r"\b(delete|remove|elimina|deprecat|drop)\b", re.IGNORECASE),
    "QUERY": re.compile(r"\b(show|list|status|what|where|how|why|explain|describe)\b", re.IGNORECASE),
}

_LANGUAGE_PATTERNS = {
    "es": re.compile(r"\b(que|como|para|desde|hacer|quiero|necesito|debería|además|donde)\b", re.IGNORECASE),
    "en": re.compile(r"\b(should|would|could|please|want|need|where|which|implement)\b", re.IGNORECASE),
}

_LAYER_REFS = {
    "l0": re.compile(r"\b(l0|overseer|go\.mod|elixir|mix\.exs|dummied)\b", re.IGNORECASE),
    "l1": re.compile(r"\b(l1|nervous|mcp_server|mcp_proxy|tools\.py|gateway)\b", re.IGNORECASE),
    "l2": re.compile(r"\b(l2|brain|daemon|orchestrat|skill|planner|memory|model)\b", re.IGNORECASE),
    "l3": re.compile(r"\b(l3|shield|audit|budget|compliance|topolog)\b", re.IGNORECASE),
    "l4": re.compile(r"\b(l4|edge|discovery|sensor|zig)\b", re.IGNORECASE),
    "l5": re.compile(r"\b(l5|muscle|driver|compactor|mojo)\b", re.IGNORECASE),
    "l6": re.compile(r"\b(l6|skin|dashboard|ui|html)\b", re.IGNORECASE),
}


def _detect_intent(prompt: str) -> str:
    """Detect primary intent from prompt via lexical patterns."""
    scores: dict[str, int] = {}
    for intent, pattern in _INTENT_PATTERNS.items():
        matches = pattern.findall(prompt)
        if matches:
            scores[intent] = len(matches)
    if not scores:
        return "QUERY"
    return max(scores, key=scores.get)


def _detect_language(prompt: str) -> str:
    """Detect natural language of the prompt."""
    scores: dict[str, int] = {}
    for lang, pattern in _LANGUAGE_PATTERNS.items():
        matches = pattern.findall(prompt)
        scores[lang] = len(matches)
    if not scores or all(v == 0 for v in scores.values()):
        return "en"
    return max(scores, key=scores.get)


def _detect_layer_refs(prompt: str) -> list[str]:
    """Detect which DUMMIE Engine layers are referenced in the prompt."""
    refs = []
    for layer, pattern in _LAYER_REFS.items():
        if pattern.search(prompt):
            refs.append(layer)
    return refs


def _build_suborders(intent: str, layer_refs: list[str], language: str) -> list[str]:
    """Generate sub-orders to inject into the enriched prompt for the cloud model."""
    suborders = []

    # Intent-specific sub-orders
    if intent == "CREATE":
        suborders.append("Generate complete implementation with proper error handling.")
        suborders.append("Include unit test skeletons for new code.")
    elif intent == "FIX":
        suborders.append("Identify root cause before applying fix.")
        suborders.append("Add regression test that would fail without the fix.")
    elif intent == "REFACTOR":
        suborders.append("Preserve all existing public interfaces.")
        suborders.append("Run existing tests to verify no regressions.")
    elif intent == "ANALYZE":
        suborders.append("Provide structured output with severity levels.")
        suborders.append("Include actionable recommendations.")
    elif intent == "DELETE":
        suborders.append("Verify no remaining references before deletion.")
        suborders.append("Use safe deletion (trash > rm).")

    # Layer-specific sub-orders
    if "l2" in layer_refs and "l3" in layer_refs:
        suborders.append("Ensure changes respect Hexagonal Architecture boundaries.")
    if len(layer_refs) > 2:
        suborders.append("This is a cross-layer change. Verify contracts between layers.")

    # Language-specific enrichment
    if language == "es":
        suborders.append("Respond in Spanish. Code comments in English.")

    return suborders


def preprocess_deterministic(prompt: str) -> PreprocessingResult:
    """
    Zero-LLM preprocessing: extract structure from the prompt using
    pure lexical/regex analysis. Always available, always fast.
    """
    started = time.perf_counter()
    intent = _detect_intent(prompt)
    language = _detect_language(prompt)
    layer_refs = _detect_layer_refs(prompt)
    suborders = _build_suborders(intent, layer_refs, language)

    # Build enriched prompt
    enriched_parts = [prompt.strip()]
    if suborders:
        enriched_parts.append("\n\n--- SYSTEM DIRECTIVES (auto-injected) ---")
        for idx, order in enumerate(suborders, 1):
            enriched_parts.append(f"{idx}. {order}")

    if layer_refs:
        enriched_parts.append(f"\nAffected layers: {', '.join(layer_refs)}")

    return PreprocessingResult(
        original_prompt=prompt,
        enriched_prompt="\n".join(enriched_parts),
        extracted_intent=intent,
        detected_language=language,
        complexity_hint="cross_layer" if len(layer_refs) > 2 else "standard",
        injected_suborders=suborders,
        context_refs=layer_refs,
        latency_ms=(time.perf_counter() - started) * 1000,
        provider="deterministic",
    )


# ─────────────────────────────────────────────
# LLM-Enhanced Preprocessing (via Ollama)
# ─────────────────────────────────────────────

_PREPROCESS_SYSTEM_PROMPT = """You are a prompt refinement engine. Given a raw user prompt:
1. Fix grammar and improve clarity.
2. Extract the primary intent (CREATE/FIX/REFACTOR/ANALYZE/DELETE/QUERY).
3. Identify which system layers are affected.
4. Add precise technical sub-orders that a cloud AI should follow.
5. Return ONLY a JSON object with keys: refined_prompt, intent, layers, suborders.
Keep the original meaning. Do not add information you don't have."""


def preprocess_with_llm(
    prompt: str,
    model: str = "",
    base_url: str = "",
    timeout: float = 5.0,
) -> PreprocessingResult:
    """
    LLM-enhanced preprocessing using a local model (Ollama).
    Falls back to deterministic if the local model is unavailable.
    """
    started = time.perf_counter()
    model = model or os.getenv("DUMMIE_LOCAL_DEEP_MODEL", "gemma4:e4b")
    base_url = (base_url or os.getenv("DUMMIE_OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")

    # Always run deterministic first as baseline
    baseline = preprocess_deterministic(prompt)

    body = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": _PREPROCESS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0},
    }).encode("utf-8")

    req = urlrequest.Request(
        f"{base_url}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        content = raw.get("message", {}).get("content") or raw.get("response") or "{}"

        # Parse JSON from LLM response
        data = _parse_json_safe(content)
        if not data:
            raise ValueError("LLM returned non-JSON response")

        refined = str(data.get("refined_prompt", prompt)).strip()
        intent = str(data.get("intent", baseline.extracted_intent)).strip().upper()
        layers = data.get("layers", baseline.context_refs)
        llm_suborders = data.get("suborders", [])

        # Merge LLM suborders with deterministic suborders
        all_suborders = list(dict.fromkeys(baseline.injected_suborders + llm_suborders))

        # Build final enriched prompt
        enriched_parts = [refined]
        if all_suborders:
            enriched_parts.append("\n\n--- SYSTEM DIRECTIVES (auto-injected) ---")
            for idx, order in enumerate(all_suborders, 1):
                enriched_parts.append(f"{idx}. {order}")
        if layers:
            enriched_parts.append(f"\nAffected layers: {', '.join(layers)}")

        return PreprocessingResult(
            original_prompt=prompt,
            enriched_prompt="\n".join(enriched_parts),
            extracted_intent=intent if intent in {i for i in _INTENT_PATTERNS} else baseline.extracted_intent,
            detected_language=baseline.detected_language,
            complexity_hint=baseline.complexity_hint,
            injected_suborders=all_suborders,
            context_refs=layers if isinstance(layers, list) else baseline.context_refs,
            latency_ms=(time.perf_counter() - started) * 1000,
            provider="ollama",
        )

    except (URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as exc:
        logger.warning("LLM preprocessing unavailable (%s), using deterministic fallback", exc)
        baseline.latency_ms = (time.perf_counter() - started) * 1000
        baseline.error = str(exc)
        return baseline


# ─────────────────────────────────────────────
# Unified Preprocessor Service
# ─────────────────────────────────────────────

class PromptPreprocessor:
    """
    Unified preprocessing service. Attempts LLM preprocessing first,
    falls back to deterministic if local model is unavailable.
    """

    def __init__(self, use_llm: bool | None = None, pre_input_hook: Any = None):
        if use_llm is None:
            self.use_llm = os.getenv("DUMMIE_PREPROCESS_LLM", "1").strip().lower() in {"1", "true", "yes"}
        else:
            self.use_llm = use_llm
        self.pre_input_hook = pre_input_hook

    def process(self, prompt: str) -> PreprocessingResult:
        """Process a raw user prompt into an enriched prompt."""
        if self.use_llm:
            result = preprocess_with_llm(prompt)
        else:
            result = preprocess_deterministic(prompt)
        result.hook_metadata = _run_optional_pre_input_hook(self.pre_input_hook, prompt, result)
        return result


def _run_optional_pre_input_hook(
    pre_input_hook: Any,
    prompt: str,
    result: PreprocessingResult,
) -> dict[str, Any]:
    if pre_input_hook is None:
        return {}

    try:
        try:
            from cognitive_hooks import CognitiveHookInput, CognitiveHookPacket
        except ImportError:  # pragma: no cover - package import fallback
            from layers.l2_brain.cognitive_hooks import CognitiveHookInput, CognitiveHookPacket

        hook_input = CognitiveHookInput(
            message=prompt,
            available_context_refs=list(result.context_refs),
            metadata={
                "preprocessor_provider": result.provider,
                "extracted_intent": result.extracted_intent,
                "detected_language": result.detected_language,
            },
        )
        if hasattr(pre_input_hook, "run"):
            hook_output = pre_input_hook.run(hook_input)
        else:
            hook_output = pre_input_hook(hook_input)

        if isinstance(hook_output, CognitiveHookPacket):
            metadata = hook_output.to_router_metadata()
        elif isinstance(hook_output, dict):
            metadata = dict(hook_output)
        elif hook_output is None:
            metadata = {}
        else:
            metadata = {"hook_output_type": type(hook_output).__name__}
        metadata["hook_status"] = "applied"
        return metadata
    except Exception as exc:
        logger.warning("Pre-input hook unavailable (%s), preserving preprocessing fallback", exc)
        return {"hook_status": "failed", "hook_error": str(exc)}


def _parse_json_safe(text: str) -> dict[str, Any]:
    """Parse JSON from potentially messy LLM output."""
    stripped = text.strip()
    # Try direct parse
    try:
        val = json.loads(stripped)
        return val if isinstance(val, dict) else {}
    except json.JSONDecodeError:
        pass
    # Try extracting from code fences
    fence = re.search(r"```(?:json)?\s*(.*?)```", stripped, flags=re.DOTALL)
    if fence:
        try:
            val = json.loads(fence.group(1).strip())
            return val if isinstance(val, dict) else {}
        except json.JSONDecodeError:
            pass
    # Try finding JSON object
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        try:
            val = json.loads(stripped[start:end + 1])
            return val if isinstance(val, dict) else {}
        except json.JSONDecodeError:
            pass
    return {}
