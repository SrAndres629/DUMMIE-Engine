import json
import os
import time
from typing import Any, Protocol, List
from urllib import request as urlrequest
from urllib.error import URLError
from dataclasses import dataclass

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
    def __init__(self, fallback_logic: Any):
        self.fallback_logic = fallback_logic

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        if task == "reasoned_rerank":
            data = {"ranked": self.fallback_logic.rank_candidates(
                goal=payload.get("goal", ""),
                candidates=payload.get("candidates", []),
                max_selected=int(payload.get("max_selected", 5)),
            )}
        elif task == "context_shaper":
            data = self.fallback_logic.shape_context_packet(
                goal=payload.get("goal", ""),
                ranked=payload.get("ranked", []),
                token_budget=int(payload.get("token_budget", 4000)),
                cloud_agent=payload.get("cloud_agent", "generic"),
            )
        else:
            data = {}
        return ReasoningResult(self.name, "deterministic", data, (time.perf_counter() - started) * 1000.0)

class OllamaGemmaProvider:
    name = "ollama"
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("DUMMIE_OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.getenv("DUMMIE_GEMMA_MODEL") or "gemma4:latest"
        self.timeout = float(timeout or os.getenv("DUMMIE_LOCAL_REASONING_TIMEOUT", "0.75"))

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        body = json.dumps({
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": f"Return only one strict JSON object. Do not include markdown. Task: {task}."},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "options": {"temperature": 0},
        }).encode("utf-8")
        req = urlrequest.Request(f"{self.base_url}/api/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            content = raw.get("message", {}).get("content") or raw.get("response") or "{}"
            return ReasoningResult(self.name, "ok", json.loads(content), (time.perf_counter() - started) * 1000.0)
        except Exception as exc:
            return ReasoningResult(self.name, "unavailable", {}, (time.perf_counter() - started) * 1000.0, str(exc))

class CascadingReasoningProvider:
    name = "cascade"
    def __init__(self, providers: List[LocalReasoningProvider]):
        self.providers = providers

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        errors = []
        for provider in self.providers:
            result = provider.complete_json(task, payload)
            if result.data and result.status in {"ok", "deterministic"}:
                return result
            if result.error:
                errors.append(f"{result.provider}:{result.error}")
        return ReasoningResult(self.name, "failed", {}, 0.0, "; ".join(errors))
