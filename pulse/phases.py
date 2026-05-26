"""Pulse phase execution — P1 Investigation, P2 Planning, P3 Builder, P4 Critic.

Production features:
- Circuit breaker for cloud models (persisted JSON, auto-reset after cooldown)
- Automatic fallback to local models when cloud is blocked or fails
- Structured JSONL production log (real token costs, not estimates)
- Cloud token cost estimation from OpenRouter usage response
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import httpx

from .config import PhaseConfig, GuardConfig
from .progress import PhaseResult

logger = logging.getLogger(__name__)

BREAKER_FILE = Path("/opt/dummie-engine/.aiwg/pulse/cloud_breaker.json")


class CloudCircuitBreaker:
    """Circuit breaker for cloud API calls.

    Persisted to .aiwg/pulse/cloud_breaker.json.
    Opens after N consecutive failures, auto-closes after cooldown.
    """

    def __init__(self, config: GuardConfig):
        self.config = config
        self.state = self._load()

    def _load(self) -> dict:
        if BREAKER_FILE.exists():
            try:
                return json.loads(BREAKER_FILE.read_text())
            except Exception:
                pass
        return {"consecutive_failures": 0, "opened_at": None, "total_cloud_failures": 0}

    def _save(self):
        BREAKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        BREAKER_FILE.write_text(json.dumps(self.state, indent=2))

    @property
    def is_open(self) -> bool:
        if self.state["opened_at"] is None:
            return False
        opened = datetime.fromisoformat(self.state["opened_at"])
        cooldown = self.config.cloud_breaker_cooldown_minutes * 60
        if (datetime.now() - opened).total_seconds() >= cooldown:
            self.state["opened_at"] = None
            self.state["consecutive_failures"] = 0
            self._save()
            logger.info("Cloud circuit breaker auto-closed (cooldown elapsed)")
            return False
        return True

    def record_success(self):
        self.state["consecutive_failures"] = 0
        self.state["opened_at"] = None
        self._save()

    def record_failure(self):
        self.state["consecutive_failures"] += 1
        self.state["total_cloud_failures"] += 1
        if self.state["consecutive_failures"] >= self.config.cloud_breaker_threshold:
            self.state["opened_at"] = datetime.now().isoformat()
            cooldown_m = self.config.cloud_breaker_cooldown_minutes
            logger.warning(
                "Cloud circuit breaker OPEN: %d consecutive failures, "
                "cloud blocked for %d minutes",
                self.state["consecutive_failures"],
                cooldown_m,
            )
        self._save()

    def get_stats(self) -> dict:
        return {
            "is_open": self.is_open,
            "consecutive_failures": self.state["consecutive_failures"],
            "total_cloud_failures": self.state["total_cloud_failures"],
            "opened_at": self.state["opened_at"],
        }


class PhaseExecutor:
    """Execute individual pulse phases with model routing and fallback."""

    def __init__(self, config: PhaseConfig, breaker: CloudCircuitBreaker = None):
        self.config = config
        self.breaker = breaker

    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        start_time = time.time()
        model_used = None
        provider_used = None
        fallback_triggered = False

        prompt = self._build_prompt(context)

        if self.config.model.startswith("openrouter/"):
            model_used, provider_used, response, errors = await self._route_cloud(
                prompt, start_time
            )
            if response is None and self.config.fallback_model:
                fallback_triggered = True
                logger.info(
                    "Falling back from cloud to local: %s → %s",
                    self.config.model,
                    self.config.fallback_model,
                )
                model_used = self.config.fallback_model
                provider_used = "ollama"
                response = await self._call_ollama_direct(
                    prompt,
                    self.config.fallback_model.replace("ollama/", ""),
                    self.config.fallback_max_tokens or self.config.max_tokens,
                )
                if response is not None:
                    errors = []
        else:
            model_used = self.config.model
            provider_used = "ollama"
            response = await self._call_ollama_direct(
                prompt,
                self.config.model.replace("ollama/", ""),
                self.config.max_tokens,
            )
            errors = []

        duration = time.time() - start_time
        tokens = response.get("tokens", 0) if response else 0

        if response:
            result = PhaseResult(
                phase_name=self.config.name,
                status="success",
                tokens_used=tokens,
                duration_seconds=duration,
                output_summary=response.get("summary", ""),
                artifacts_created=response.get("artifacts", []),
                errors=errors,
            )
            result.model_used = model_used
            result.provider_used = provider_used
            result.fallback_triggered = fallback_triggered
            result.cloud_tokens = tokens if provider_used == "openrouter" else 0
            result.local_tokens = tokens if provider_used == "ollama" else 0
            return result

        return PhaseResult(
            phase_name=self.config.name,
            status="failed",
            tokens_used=0,
            duration_seconds=duration,
            output_summary="All model calls failed",
            errors=errors if errors else ["All model calls failed"],
        )

    async def _route_cloud(self, prompt: str, start_time: float) -> tuple:
        """Route cloud call with circuit breaker check."""
        errors = []

        if self.breaker and self.breaker.is_open:
            logger.warning(
                "Cloud circuit breaker open — skipping cloud call for %s",
                self.config.name,
            )
            return None, None, None, ["Cloud circuit breaker open"]

        try:
            response = await self._call_openrouter(prompt)
            if response:
                if self.breaker:
                    self.breaker.record_success()
                return (
                    self.config.model,
                    "openrouter",
                    response,
                    [],
                )
            errors.append("OpenRouter returned no response")
        except Exception as e:
            errors.append(f"OpenRouter: {e}")

        if self.breaker:
            self.breaker.record_failure()

        return None, None, None, errors

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        prompts = {
            "investigation": (
                "You are DUMMIE Pulse Engine — Investigation Phase.\n\n"
                "Analyze the current state and identify actionable opportunities.\n\n"
                f"Context: {context.get('system_state', 'Unknown')}\n"
                f"Recent: {context.get('recent_activity', 'None')}\n\n"
                "Provide structured findings with priority levels and estimated effort."
            ),
            "planning": (
                "You are DUMMIE Pulse Engine — Planning Phase.\n\n"
                "Create a strategic execution plan based on investigation results.\n\n"
                f"Findings: {context.get('investigation_results', 'None')}\n\n"
                "Provide numbered, actionable steps with effort/impact estimates."
            ),
            "builder": (
                "You are DUMMIE Pulse Engine — Builder Phase.\n\n"
                "Implement the planned changes using available tools.\n\n"
                f"Plan: {context.get('plan', context.get('planning_results', 'None'))}\n\n"
                "Execute changes and report concrete results."
            ),
            "critic": (
                "You are DUMMIE Pulse Engine — Critic Phase.\n\n"
                "Review implemented changes critically and objectively.\n\n"
                f"Changes: {context.get('implemented_changes', context.get('builder_results', 'None'))}\n\n"
                "Provide structured feedback: what risks exist, what was missed, what to improve."
            ),
        }
        return prompts.get(self.config.name, f"Execute {self.config.name} phase")

    async def _call_openrouter(self, prompt: str) -> Optional[Dict[str, Any]]:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        model_name = self.config.model.replace("openrouter/", "")
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.config.max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "summary": content[:1000],
                "raw_response": content,
                "tokens": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "cost_usd": self._estimate_cost(usage),
                "artifacts": [],
            }

    async def _call_ollama_direct(
        self, prompt: str, model_name: str, max_tokens: int
    ) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": max_tokens},
                    },
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "summary": data.get("response", "")[:1000],
                    "raw_response": data.get("response", ""),
                    "tokens": data.get("eval_count", 0),
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "cost_usd": 0.0,
                    "artifacts": [],
                }
        except Exception:
            return None

    def _estimate_cost(self, usage: dict) -> float:
        model = self.config.model.replace("openrouter/", "")
        pricing = {
            "deepseek/deepseek-v4-pro": (2.00, 8.00),
            "anthropic/claude-sonnet-4": (2.00, 8.00),
            "google/gemini-2.5-flash": (0.15, 0.30),
        }
        prompt_price, completion_price = pricing.get(model, (0, 0))
        ptok = usage.get("prompt_tokens", 0)
        ctok = usage.get("completion_tokens", 0)
        return (ptok / 1_000_000 * prompt_price) + (ctok / 1_000_000 * completion_price)
