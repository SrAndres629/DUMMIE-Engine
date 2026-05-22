import time, logging
from typing import Optional
from .base import BaseModelAdapter, ModelSpec, ModelType, OntologyClass

logger = logging.getLogger("dummie-mcp.models.adapters.cross_encoder")


class CrossEncoderAdapter(BaseModelAdapter):
    def __init__(self, spec: ModelSpec):
        super().__init__(spec)
        self._model = None

    async def _load_model(self):
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(self.spec.model_id)

    async def rerank(
        self, query: str, candidates: list[str], top_k: int = 5
    ) -> list[tuple[str, float]]:
        self.touch()
        t0 = time.time()
        pairs = [(query, c) for c in candidates]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
        elapsed = (time.time() - t0) * 1000
        self.metrics.total_inference_ms += elapsed
        return ranked[:top_k]

    async def health(self) -> dict:
        return {"model_id": self.spec.model_id, "state": self.state.value}
