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
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0

class LocalReasoningProvider(Protocol):
    name: str
    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        ...

class DeterministicReasoningProvider:
    name = "deterministic"
    def __init__(self, fallback_logic: Any = None):
        if fallback_logic is None:
            from layers.l2_brain.domain.reasoning_logic import ReasoningLogic
            fallback_logic = ReasoningLogic
        self.fallback_logic = fallback_logic

    def parse_json_response(self, text: str) -> dict[str, Any]:
        import re
        cleaned = text.strip()
        if "```json" in cleaned:
            match = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)
        elif "```" in cleaned:
            match = re.search(r"```\s*(.*?)\s*```", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)
        cleaned = re.sub(r"^[^{]*", "", cleaned.strip())
        cleaned = re.sub(r"[^}]*$", "", cleaned.strip())
        try:
            return json.loads(cleaned)
        except Exception:
            return {}

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
            
            # Ollama token extraction
            prompt_t = raw.get("prompt_eval_count", 0)
            completion_t = raw.get("eval_count", 0)
            
            return ReasoningResult(
                self.name, "ok", json.loads(content), 
                (time.perf_counter() - started) * 1000.0,
                prompt_tokens=prompt_t,
                completion_tokens=completion_t
            )
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

class OpenAICompatibleProvider:
    name = "openai"
    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("DUMMIE_OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.getenv("DUMMIE_OPENAI_API_KEY") or "sk-fake"
        self.model = model or os.getenv("DUMMIE_OPENAI_MODEL") or "gpt-4o"
        self.timeout = float(timeout or os.getenv("DUMMIE_LOCAL_REASONING_TIMEOUT", "10.0"))

    def complete_json(self, task: str, payload: dict[str, Any]) -> ReasoningResult:
        started = time.perf_counter()
        body = json.dumps({
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": f"Return only one strict JSON object. Task: {task}."},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "temperature": 0,
        }).encode("utf-8")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        req = urlrequest.Request(f"{self.base_url}/chat/completions", data=body, headers=headers, method="POST")
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            
            usage = raw.get("usage", {})
            content = raw.get("choices", [{}])[0].get("message", {}).get("content") or "{}"
            
            return ReasoningResult(
                self.name, "ok", json.loads(content), 
                (time.perf_counter() - started) * 1000.0,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                cached_tokens=usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
            )
        except Exception as exc:
            return ReasoningResult(self.name, "unavailable", {}, (time.perf_counter() - started) * 1000.0, str(exc))
