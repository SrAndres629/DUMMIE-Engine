import time, logging, numpy as np
from typing import Optional
from threading import Lock
from .base import BaseModelAdapter, ModelSpec, ModelType, OntologyClass

logger = logging.getLogger("dummie-mcp.models.adapters.fastembed")


class FastEmbedAdapter(BaseModelAdapter):
    _instances: dict[str, "FastEmbedAdapter"] = {}
    _lock = Lock()

    def __init__(self, spec: ModelSpec):
        super().__init__(spec)
        self._model_instance = None
        self._dimensions = 384

    @classmethod
    def get_instance(cls, spec: ModelSpec) -> "FastEmbedAdapter":
        key = spec.model_id
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(spec)
            return cls._instances[key]

    async def _load_model(self):
        from fastembed import TextEmbedding

        self._model_instance = TextEmbedding(model_name=self.spec.model_id)
        self._dimensions = 384

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        self.touch()
        t0 = time.time()
        result = list(self._model_instance.embed(texts))
        elapsed = (time.time() - t0) * 1000
        self.metrics.total_inference_ms += elapsed
        return result

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def similarity_batch(
        self, query: np.ndarray, candidates: list[np.ndarray]
    ) -> list[float]:
        return [self.similarity(query, c) for c in candidates]

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def health(self) -> dict:
        return {
            "model_id": self.spec.model_id,
            "state": self.state.value,
            "dimensions": self._dimensions,
        }
