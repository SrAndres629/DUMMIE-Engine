import json, logging
from typing import Optional
from .base import BaseModelAdapter, ModelSpec, ModelType, OntologyClass

logger = logging.getLogger("dummie-mcp.models.adapters.ollama")


class OllamaAdapter(BaseModelAdapter):
    def __init__(self, spec: ModelSpec, base_url: str = "http://localhost:11434"):
        super().__init__(spec)
        self.base_url = base_url.rstrip("/")
        self._client = None

    async def _load_model(self):
        import ollama

        self._client = ollama.AsyncClient(host=self.base_url)
        await self._client.list()
        logger.info(f"Ollama connected at {self.base_url}")

    def _build_prompt(self, system: str, user: str) -> list[dict]:
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    async def generate(self, system: str, user: str, **kwargs) -> str:
        self.touch()
        import time

        t0 = time.time()
        response = await self._client.chat(
            model=self.spec.model_id,
            messages=self._build_prompt(system, user),
            options={
                "num_predict": kwargs.get("max_tokens", 512),
                "temperature": kwargs.get("temperature", 0.1),
            },
        )
        elapsed = (time.time() - t0) * 1000
        self.metrics.total_inference_ms += elapsed
        return response["message"]["content"]

    async def generate_json(self, system: str, user: str, **kwargs) -> dict:
        raw = await self.generate(system, user, **kwargs)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw": cleaned, "error": "JSON parse failed"}

    async def health(self) -> dict:
        try:
            models = await self._client.list()
            return {
                "model_id": self.spec.model_id,
                "state": self.state.value,
                "models": list(models.get("models", [])),
            }
        except Exception as e:
            return {"model_id": self.spec.model_id, "state": "error", "error": str(e)}
