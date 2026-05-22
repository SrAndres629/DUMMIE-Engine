from abc import ABC, abstractmethod
from typing import Optional
from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.models.model_registry import ModelRegistry


class BaseRoutingStrategy(ABC):
    name: str = "base"

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry
        self._adapter = None

    async def _ensure_loaded(self, model_id: str):
        if self._adapter is not None:
            return
        if self.registry:
            self._adapter = self.registry.get_or_create(model_id)
        else:
            self._adapter = await self._create_adapter_standalone(model_id)
        load = getattr(self._adapter, "ensure_loaded", None)
        if load:
            await load() if hasattr(load, "__call__") else load

    async def _create_adapter_standalone(self, model_id: str):
        from dummie_sdk.config import get_config

        cfg = get_config()
        spec = cfg.get_model(model_id)
        if not spec:
            raise ValueError(f"Model '{model_id}' not in config")
        if spec.provider == "ollama":
            from dummie_sdk.models.adapters.ollama_adapter import OllamaAdapter

            return OllamaAdapter(spec)
        elif spec.provider == "fastembed":
            from dummie_sdk.models.adapters.fastembed_adapter import FastEmbedAdapter

            return FastEmbedAdapter(spec)
        elif spec.provider == "sentence_transformers":
            from dummie_sdk.models.adapters.cross_encoder_adapter import (
                CrossEncoderAdapter,
            )

            return CrossEncoderAdapter(spec)
        raise ValueError(f"Unknown provider '{spec.provider}'")

    @abstractmethod
    async def execute(self, query: str) -> RoutingResult: ...
