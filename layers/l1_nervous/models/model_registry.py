import json, os, logging
from pathlib import Path
from typing import Optional, Type
from .adapters.base import BaseModelAdapter, ModelSpec, ModelType, OntologyClass
from .adapters.fastembed_adapter import FastEmbedAdapter
from .adapters.ollama_adapter import OllamaAdapter
from .adapters.cross_encoder_adapter import CrossEncoderAdapter

logger = logging.getLogger("dummie-mcp.models.registry")

ADAPTER_MAP = {
    "fastembed": FastEmbedAdapter,
    "ollama": OllamaAdapter,
    "cross_encoder": CrossEncoderAdapter,
}

DEFAULT_CONFIG = {
    "models": [
        {
            "id": "BAAI/bge-small-en-v1.5",
            "type": "embedding",
            "adapter": "fastembed",
            "ontology": "semantic",
            "priority": 1,
            "vram_mb": 0,
            "ram_mb": 200,
        },
        {
            "id": "gemma3:1b",
            "type": "llm",
            "adapter": "ollama",
            "ontology": "reasoning",
            "priority": 3,
            "vram_mb": 815,
            "ram_mb": 200,
        },
        {
            "id": "cross-encoder/ms-marco-MiniLM-L-2-v2",
            "type": "reranker",
            "adapter": "cross_encoder",
            "ontology": "search",
            "priority": 2,
            "vram_mb": 80,
            "ram_mb": 100,
        },
        {
            "id": "gemma4:e4b",
            "type": "llm",
            "adapter": "ollama",
            "ontology": "reasoning",
            "priority": 3,
            "vram_mb": 3000,
            "ram_mb": 500,
        },
    ]
}


class ModelRegistry:
    def __init__(self, config_path: str = None):
        self._adapters: dict[str, BaseModelAdapter] = {}
        self._specs: dict[str, ModelSpec] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str = None):
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                data = json.load(f)
        else:
            data = DEFAULT_CONFIG
        for m in data.get("models", []):
            spec = ModelSpec(
                model_id=m["id"],
                model_type=ModelType(m["type"]),
                ontology=OntologyClass(m.get("ontology", "semantic")),
                priority=m.get("priority", 5),
                vram_mb=m.get("vram_mb", 0),
                ram_mb=m.get("ram_mb", 0),
                config=m.get("config", {}),
            )
            self._specs[spec.model_id] = spec

    def get_adapter(self, model_id: str) -> Optional[BaseModelAdapter]:
        return self._adapters.get(model_id)

    def create_adapter(self, model_id: str) -> BaseModelAdapter:
        if model_id in self._adapters:
            return self._adapters[model_id]
        spec = self._specs.get(model_id)
        if not spec:
            raise ValueError(
                f"Model '{model_id}' not in registry. Available: {list(self._specs.keys())}"
            )
        adapter_cls = self._resolve_adapter(spec)
        adapter = adapter_cls(spec)
        self._adapters[model_id] = adapter
        return adapter

    def get_or_create(self, model_id: str) -> BaseModelAdapter:
        return self.get_adapter(model_id) or self.create_adapter(model_id)

    def _resolve_adapter(self, spec: ModelSpec) -> Type[BaseModelAdapter]:
        if spec.model_type == ModelType.EMBEDDING:
            return ADAPTER_MAP["fastembed"]
        elif spec.model_type == ModelType.LLM:
            return ADAPTER_MAP["ollama"]
        elif spec.model_type == ModelType.RERANKER:
            return ADAPTER_MAP["cross_encoder"]
        raise ValueError(f"Unknown model type {spec.model_type} for {spec.model_id}")

    def list_models(self) -> list[dict]:
        return [
            {
                "id": m.model_id,
                "type": m.model_type.value,
                "ontology": m.ontology.value,
                "state": self._adapters[m.model_id].state.value
                if m.model_id in self._adapters
                else "unloaded",
            }
            for m in self._specs.values()
        ]

    def get_best_for_type(
        self, model_type: ModelType, min_priority: int = 5
    ) -> Optional[BaseModelAdapter]:
        candidates = [
            s
            for s in self._specs.values()
            if s.model_type == model_type and s.priority <= min_priority
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x.priority)
        return self.get_or_create(candidates[0].model_id)
