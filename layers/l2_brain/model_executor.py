import httpx
import logging
import time
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from model_router import ModelConfig, ModelTier, RoutingDecision

logger = logging.getLogger("brain.executor")

@dataclass
class ModelResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    model_id: str
    success: bool
    error: Optional[str] = None

class ModelExecutor:
    """
    [L2_BRAIN] Ejecutor unificado de inferencia.
    Sabe hablar con diferentes protocolos (Ollama, OpenAI-Compatible).
    """
    def __init__(self, token_ledger: Optional[Any] = None):
        self.token_ledger = token_ledger

    async def execute(self, decision: RoutingDecision, prompt: str, system_prompt: str = "") -> ModelResponse:
        model_id = decision.model_id
        # In practice, the decision should contain the full ModelConfig
        # For now, we'll assume we can fetch it or it's passed
        # Let's simplify: pass the ModelConfig instead of decision or just assume a registry lookup
        # Better: let's modify the execute signature slightly or just use the model_id
        pass # To be implemented below

    async def execute_config(self, config: ModelConfig, prompt: str, system_prompt: str = "", concept: str = "general") -> ModelResponse:
        start_time = time.perf_counter()
        
        try:
            if config.provider == "ollama":
                res = await self._execute_ollama(config, prompt, system_prompt)
            elif config.provider == "openai_compat":
                res = await self._execute_openai_compat(config, prompt, system_prompt)
            else:
                raise ValueError(f"Unknown provider: {config.provider}")
            
            latency = (time.perf_counter() - start_time) * 1000
            res.latency_ms = latency
            
            if self.token_ledger and res.success:
                self.token_ledger.record_usage(
                    model_id=res.model_id,
                    tier=config.tier.value,
                    prompt_tokens=res.prompt_tokens,
                    completion_tokens=res.completion_tokens,
                    concept=concept,
                    cost_per_1k=config.cost_per_1k_tokens
                )
            
            return res
            
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            logger.error(f"Execution failed for {config.model_id}: {e}")
            return ModelResponse("", 0, 0, latency, config.model_id, False, str(e))

    async def _execute_ollama(self, config: ModelConfig, prompt: str, system_prompt: str) -> ModelResponse:
        payload = {
            "model": config.model_id,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"num_predict": config.max_tokens}
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{config.base_url}/api/generate",
                json=payload,
                timeout=config.timeout_s
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Ollama gives tokens in 'prompt_eval_count' and 'eval_count'
            return ModelResponse(
                text=data.get("response", ""),
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                latency_ms=0,
                model_id=config.model_id,
                success=True
            )

    async def _execute_openai_compat(self, config: ModelConfig, prompt: str, system_prompt: str) -> ModelResponse:
        api_key = os.getenv(config.api_key_env)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": config.model_id,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": 0.0
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=config.timeout_s
            )
            resp.raise_for_status()
            data = resp.json()
            
            usage = data.get("usage", {})
            choice = data.get("choices", [{}])[0]
            text = choice.get("message", {}).get("content", "")
            
            return ModelResponse(
                text=text,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                latency_ms=0,
                model_id=config.model_id,
                success=True
            )
