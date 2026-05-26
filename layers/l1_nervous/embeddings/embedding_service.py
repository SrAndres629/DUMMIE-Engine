"""Embedding service with GPU acceleration (spec 211)."""

import numpy as np


class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self._device = self._detect_device()

    @staticmethod
    def _detect_device() -> str:
        import os

        if os.environ.get("CUDA_VISIBLE_DEVICES") is not None:
            return "cuda"
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        return "cpu"

    @property
    def model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            providers = None
            if self._device == "cuda":
                providers = ["CUDAExecutionProvider"]
            self._model = TextEmbedding(
                model_name=self.model_name,
                providers=providers,
            )
        return self._model

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        return list(self.model.embed(texts))

    def embed_one(self, text: str) -> np.ndarray:
        return list(self.model.embed([text]))[0]

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @property
    def dimensions(self) -> int:
        return 384
