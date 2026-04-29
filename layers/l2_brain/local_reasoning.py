from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import time
from typing import Any, Protocol
from urllib import request as urlrequest
from urllib.error import URLError

def load_dotenv_simple():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    if not os.path.exists(env_path):
        env_path = os.path.abspath(os.path.join(os.getcwd(), ".env"))
        
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val

load_dotenv_simple()


@dataclass
class ReasoningResult:
    provider: str
    status: str
    data: dict[str, Any]
    latency_ms: float = 0.0
    error: str = ""


class LocalReasoningProvider(Protocol):
    name: str

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        ...


class DeterministicReasoningProvider:
    name = "deterministic"

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        if task == "reasoned_rerank":
            data = {
                "ranked": rank_candidates(
                    goal=payload.get("goal", ""),
                    candidates=payload.get("candidates", []),
                    max_selected=int(payload.get("max_selected", 5)),
                )
            }
        elif task == "context_shaper":
            data = shape_context_packet(
                goal=payload.get("goal", ""),
                ranked=payload.get("ranked", []),
                token_budget=int(payload.get("token_budget", 4000)),
                cloud_agent=payload.get("cloud_agent", "generic"),
            )
        else:
            data = {}
        return ReasoningResult(
            provider=self.name,
            status="deterministic",
            data=data,
            latency_ms=(time.perf_counter() - started) * 1000.0,
        )

    def parse_json_response(self, text: str) -> dict[str, Any]:
        return parse_json_object(text)


class OllamaGemmaProvider:
    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("DUMMIE_OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.getenv("DUMMIE_GEMMA_MODEL") or "gemma4:latest"
        self.timeout = float(timeout or os.getenv("DUMMIE_LOCAL_REASONING_TIMEOUT", "45"))

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        body = json.dumps(
            {
                "model": self.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": _system_prompt(task)},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                "options": {
                    "temperature": 0,
                    "num_ctx": 8192,
                    "num_thread": int(os.getenv("DUMMIE_OLLAMA_THREADS", "4"))
                },
            }
        ).encode("utf-8")
        req = urlrequest.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            content = raw.get("message", {}).get("content") or raw.get("response") or "{}"
            data = parse_json_object(content)
            return ReasoningResult(self.name, "ok", data, (time.perf_counter() - started) * 1000.0)
        except Exception as exc:
            return ReasoningResult(self.name, "unavailable", {}, (time.perf_counter() - started) * 1000.0, str(exc))


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("DUMMIE_OPENAI_COMPAT_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("DUMMIE_OPENAI_COMPAT_API_KEY") or ""
        self.model = model or os.getenv("DUMMIE_GEMMA_MODEL") or "gemma4"
        self.timeout = float(timeout or os.getenv("DUMMIE_LOCAL_REASONING_TIMEOUT", "45"))

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        if not self.base_url:
            return ReasoningResult(self.name, "unconfigured", {}, 0.0, "missing DUMMIE_OPENAI_COMPAT_BASE_URL")
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": _system_prompt(task)},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urlrequest.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            content = raw["choices"][0]["message"]["content"]
            data = parse_json_object(content)
            return ReasoningResult(self.name, "ok", data, (time.perf_counter() - started) * 1000.0)
        except (KeyError, IndexError, URLError, TimeoutError, ValueError, OSError) as exc:
            return ReasoningResult(self.name, "unavailable", {}, (time.perf_counter() - started) * 1000.0, str(exc))


class CascadingReasoningProvider:
    name = "cascade"

    def __init__(self, providers: list[LocalReasoningProvider]):
        self.providers = providers

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        errors = []
        for provider in self.providers:
            result = provider.complete_json(task, payload)
            if result.data and result.status in {"ok", "deterministic"}:
                return result
            if result.error:
                errors.append(f"{result.provider}:{result.error}")
        fallback = DeterministicReasoningProvider().complete_json(task, payload)
        fallback.error = "; ".join(errors)
        return fallback


def build_local_reasoning_provider() -> LocalReasoningProvider:
    configured = os.getenv("DUMMIE_LOCAL_REASONING_PROVIDER", "auto").strip().lower()
    if configured == "deterministic":
        return DeterministicReasoningProvider()
    if configured == "ollama":
        return CascadingReasoningProvider([OllamaGemmaProvider(), DeterministicReasoningProvider()])
    if configured in {"openai", "openai-compatible", "openai_compatible"}:
        return CascadingReasoningProvider([OpenAICompatibleProvider(), DeterministicReasoningProvider()])
    return CascadingReasoningProvider(
        [OllamaGemmaProvider(), OpenAICompatibleProvider(), DeterministicReasoningProvider()]
    )


class LocalReasoningService:
    def __init__(self, provider: LocalReasoningProvider | None = None):
        self.provider = provider or build_local_reasoning_provider()

    def reasoned_rerank(
        self,
        goal: str,
        candidates: list[dict[str, Any]],
        max_selected: int = 5,
        mode: str = "shadow",
    ) -> dict[str, Any]:
        payload = {
            "goal": goal,
            "candidates": candidates,
            "max_selected": max_selected,
            "mode": mode,
        }
        result = self.provider.complete_json("reasoned_rerank", payload)
        ranked = result.data.get("ranked") if isinstance(result.data, dict) else None
        if not isinstance(ranked, list):
            ranked = rank_candidates(goal, candidates, max_selected)
        return {
            "provider": result.provider,
            "provider_status": result.status,
            "latency_ms": result.latency_ms,
            "mode": mode,
            "ranked": normalize_ranked(goal, ranked, candidates, max_selected),
            "error": result.error,
        }

    def context_shaper(
        self,
        goal: str,
        ranked: list[dict[str, Any]],
        token_budget: int = 4000,
        cloud_agent: str = "generic",
    ) -> dict[str, Any]:
        payload = {
            "goal": goal,
            "ranked": ranked,
            "token_budget": token_budget,
            "cloud_agent": cloud_agent,
        }
        result = self.provider.complete_json("context_shaper", payload)
        data = result.data if isinstance(result.data, dict) and result.data else shape_context_packet(
            goal, ranked, token_budget, cloud_agent
        )
        packet = shape_context_packet(
            goal=data.get("task_brief") or goal,
            ranked=ranked,
            token_budget=token_budget,
            cloud_agent=cloud_agent,
        )
        packet.update({k: v for k, v in data.items() if k in packet and v})
        packet["estimated_tokens"] = min(int(packet.get("estimated_tokens", 0) or 0), token_budget)
        packet["provider"] = result.provider
        packet["provider_status"] = result.status
        packet["latency_ms"] = result.latency_ms
        packet["error"] = result.error
        return packet


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        stripped = fence.group(1).strip()
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            value = json.loads(stripped[start : end + 1])
            return value if isinstance(value, dict) else {}
    return {}


def rank_candidates(goal: str, candidates: list[dict[str, Any]], max_selected: int = 5) -> list[dict[str, Any]]:
    ranked = []
    for candidate in candidates:
        side_effect = str(candidate.get("side_effect_level") or "read").lower()
        score = float(candidate.get("score") or 0.0)
        overlap = lexical_overlap(goal, candidate_text(candidate))
        penalty = side_effect_penalty(side_effect)
        if side_effect in {"write", "external"} and overlap >= 0.25:
            penalty = min(penalty, 0.05)
        score += overlap * 0.5
        if side_effect == "write" and any(token in _tokens(goal) for token in ["persist", "crystallize", "feedback", "lesson", "log"]):
            score += 0.15
        score -= penalty
        normalized = dict(candidate)
        normalized["score"] = round(max(0.0, min(1.0, score)), 4)
        normalized["risk"] = risk_for_side_effect(side_effect)
        normalized["why"] = normalized.get("why") or _why_for_candidate(goal, normalized)
        normalized["missing_context"] = normalized.get("missing_context", [])
        normalized["recommended_next_step"] = normalized.get("recommended_next_step") or "use_if_schema_matches"
        ranked.append(normalized)
    ranked.sort(key=lambda item: item.get("score", 0.0), reverse=True)
    return ranked[: max(1, max_selected)]


def normalize_ranked(
    goal: str,
    ranked: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    max_selected: int,
) -> list[dict[str, Any]]:
    by_id = {str(item.get("id")): item for item in candidates}
    normalized = []
    for item in ranked:
        item_id = str(item.get("id") or item.get("target") or "")
        if not item_id:
            continue
        merged = {**by_id.get(item_id, {}), **item}
        side_effect = str(merged.get("side_effect_level") or "read").lower()
        merged["score"] = round(max(0.0, min(1.0, float(merged.get("score") or 0.0))), 4)
        merged["risk"] = merged.get("risk") or risk_for_side_effect(side_effect)
        merged["why"] = merged.get("why") or _why_for_candidate(goal, merged)
        merged["missing_context"] = merged.get("missing_context") or []
        merged["recommended_next_step"] = merged.get("recommended_next_step") or "use_if_schema_matches"
        normalized.append(merged)
    if not normalized:
        return rank_candidates(goal, candidates, max_selected)
    normalized.sort(key=lambda item: item.get("score", 0.0), reverse=True)
    return normalized[: max(1, max_selected)]


def shape_context_packet(
    goal: str,
    ranked: list[dict[str, Any]],
    token_budget: int = 4000,
    cloud_agent: str = "generic",
) -> dict[str, Any]:
    selected = [str(item.get("id") or item.get("target")) for item in ranked if item.get("id") or item.get("target")]
    evidence: list[str] = []
    open_unknowns: list[str] = []
    for item in ranked:
        evidence.extend([str(ref) for ref in item.get("evidence_refs", [])])
        open_unknowns.extend([str(ref) for ref in item.get("missing_context", [])])
    packet = {
        "task_brief": truncate_text(goal.strip(), max(80, token_budget * 4 // 3)),
        "selected_tools": selected[:5],
        "evidence_bundle": list(dict.fromkeys(evidence))[:10],
        "open_unknowns": list(dict.fromkeys(open_unknowns))[:10],
        "execution_hint": f"Prepare {cloud_agent} with selected tools before cloud execution.",
        "estimated_tokens": 0,
    }
    packet["estimated_tokens"] = min(estimate_tokens(json.dumps(packet, ensure_ascii=False)), token_budget)
    return packet


def candidate_text(candidate: dict[str, Any]) -> str:
    return " ".join(
        str(candidate.get(key, ""))
        for key in ("id", "target", "text", "description", "why", "source")
        if candidate.get(key)
    )


def lexical_overlap(left: str, right: str) -> float:
    left_tokens = set(_tokens(left))
    right_tokens = set(_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def side_effect_penalty(side_effect: str) -> float:
    return {
        "read": 0.0,
        "none": 0.0,
        "write": 0.15,
        "external": 0.2,
        "destructive": 0.4,
    }.get(side_effect, 0.1)


def risk_for_side_effect(side_effect: str) -> str:
    if side_effect == "destructive":
        return "high"
    if side_effect in {"write", "external"}:
        return "medium"
    return "low"


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 3)].rstrip() + "..."


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(token) > 2]


def _why_for_candidate(goal: str, candidate: dict[str, Any]) -> str:
    overlap = lexical_overlap(goal, candidate_text(candidate))
    if overlap > 0:
        return f"shares {overlap:.2f} lexical overlap with the goal"
    return "selected by baseline score and low side-effect profile"


def _system_prompt(task: str) -> str:
    return (
        "Return only one strict JSON object. Do not include markdown. "
        f"Task: {task}. Keep scores between 0 and 1 and include concise reasons."
    )
