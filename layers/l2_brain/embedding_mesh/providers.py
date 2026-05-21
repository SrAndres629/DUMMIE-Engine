# Spec Reference: 192_embedding_mesh_foundation
import abc
import hashlib
import logging
import math
from typing import Optional

from .contracts import (
    EmbeddingCapability,
    EmbeddingRequest,
    EmbeddingResponse,
    VectorSpace,
    fallback_vector_space,
)

logger = logging.getLogger("brain.embedding_mesh.providers")

_MODEL_CACHE: dict = {}


class IEmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError


class DeterministicFallbackProvider(IEmbeddingProvider):
    """
    Deterministic hash-based fallback provider.

    Guarantees stable vectors offline while explicitly marking degraded state.
    """

    def __init__(
        self,
        dimensions: int = 384,
        capability: EmbeddingCapability = EmbeddingCapability.FALLBACK,
    ):
        self.dimensions = dimensions
        self.capability = capability

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        content = request.content or ""
        payload_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        extended_hash = payload_hash
        while len(extended_hash) < self.dimensions * 2:
            extended_hash += hashlib.sha256(extended_hash.encode("utf-8")).hexdigest()

        raw_values = []
        for i in range(self.dimensions):
            byte_val = int(extended_hash[i * 2 : i * 2 + 2], 16)
            raw_values.append(float(byte_val) / 255.0)

        sq_sum = sum(v * v for v in raw_values)
        norm = math.sqrt(sq_sum)
        if norm > 0.0:
            vector = [v / norm for v in raw_values]
        else:
            vector = [0.0] * self.dimensions

        return EmbeddingResponse(
            vector=vector,
            dimensions=self.dimensions,
            model_used="deterministic-sha256-projection",
            capability=self.capability,
            vector_space=fallback_vector_space(self.dimensions),
            normalized=True,
            degraded=True,
            reason="operating under offline deterministic hash projection fallback",
            payload_hash=payload_hash,
        )


class LegacyEmbeddingProviderAdapter(IEmbeddingProvider):
    """
    Compatibility adapter for the existing EmbeddingProvider runtime.

    This adapter never downloads models and degrades to deterministic fallback
    when legacy provider cannot initialize its local fastembed stack.
    """

    def __init__(self):
        self._fallback = DeterministicFallbackProvider(
            dimensions=384,
            capability=EmbeddingCapability.TEXT_FAST,
        )
        self._legacy_disabled = False
        self._warned_disabled = False

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        if self._legacy_disabled:
            response = self._fallback.embed(request)
            response.reason = "legacy embedding provider previously failed; deterministic fallback active"
            return response

        content = request.content or ""
        payload_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        try:
            from layers.l2_brain.embedding_provider import EmbeddingProvider

            vector = EmbeddingProvider.generate_vector(content)
            return EmbeddingResponse(
                vector=vector,
                dimensions=len(vector),
                model_used="BAAI/bge-small-en-v1.5",
                capability=EmbeddingCapability.TEXT_FAST,
                vector_space=VectorSpace.TEXT_FAST_BGE_SMALL_384,
                normalized=True,
                degraded=False,
                reason="",
                payload_hash=payload_hash,
            )
        except Exception as exc:  # pragma: no cover - exercised via tests indirectly
            self._legacy_disabled = True
            if not self._warned_disabled:
                logger.warning(
                    "LegacyEmbeddingProviderAdapter degraded to fallback: %s", exc
                )
                self._warned_disabled = True
            response = self._fallback.embed(request)
            response.reason = f"legacy embedding provider unavailable: {exc}"
            return response


class FastEmbedTextProvider(IEmbeddingProvider):
    """
    Local fastembed provider with deterministic fallback.

    No automatic model downloading is performed by this wrapper.
    If runtime environment has no local model, degraded fallback is returned.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self._fallback_provider = DeterministicFallbackProvider(
            dimensions=384,
            capability=EmbeddingCapability.TEXT_FAST,
        )

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        content = request.content or ""
        payload_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        try:
            model = self._get_model()
            embeddings_gen = model.embed([content])
            vector_np = next(embeddings_gen)
            vector_list = vector_np.tolist()

            return EmbeddingResponse(
                vector=vector_list,
                dimensions=len(vector_list),
                model_used=self.model_name,
                capability=EmbeddingCapability.TEXT_FAST,
                vector_space=VectorSpace.TEXT_FAST_BGE_SMALL_384,
                normalized=True,
                degraded=False,
                reason="",
                payload_hash=payload_hash,
            )
        except Exception as exc:
            logger.warning("FastEmbedTextProvider degraded to fallback: %s", exc)
            fallback_response = self._fallback_provider.embed(request)
            fallback_response.reason = f"fastembed unavailable/offline: {exc}"
            return fallback_response


class FastEmbedCodeProvider(IEmbeddingProvider):
    """
    CODE embedding provider using local fastembed (same model as TEXT_FAST).

    Uses shared model cache to avoid loading duplicate model instances.
    Stores vectors under CODE_LOCAL_768 vector space for semantic isolation.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._fallback_provider = DeterministicFallbackProvider(
            dimensions=384,
            capability=EmbeddingCapability.CODE,
        )

    def _get_model(self):
        if self.model_name not in _MODEL_CACHE:
            from fastembed import TextEmbedding

            _MODEL_CACHE[self.model_name] = TextEmbedding(model_name=self.model_name)
        return _MODEL_CACHE[self.model_name]

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        content = request.content or ""
        payload_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        try:
            model = self._get_model()
            embeddings_gen = model.embed([content])
            vector_np = next(embeddings_gen)
            vector_list = vector_np.tolist()

            return EmbeddingResponse(
                vector=vector_list,
                dimensions=len(vector_list),
                model_used=self.model_name,
                capability=EmbeddingCapability.CODE,
                vector_space=VectorSpace.CODE_LOCAL_768,
                normalized=True,
                degraded=False,
                reason="",
                payload_hash=payload_hash,
            )
        except Exception as exc:
            logger.warning("FastEmbedCodeProvider degraded to fallback: %s", exc)
            fallback_response = self._fallback_provider.embed(request)
            fallback_response.reason = f"fastembed unavailable/offline: {exc}"
            return fallback_response


class PlaceholderCapabilityProvider(IEmbeddingProvider):
    """
    Placeholder provider for capabilities not yet wired to real local models.
    """

    def __init__(
        self,
        capability: EmbeddingCapability,
        dimensions: int = 384,
        model_tag: Optional[str] = None,
    ):
        self.capability = capability
        self._fallback = DeterministicFallbackProvider(
            dimensions=dimensions, capability=capability
        )
        self.model_tag = model_tag or f"placeholder-{capability.value.lower()}"

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        response = self._fallback.embed(request)
        response.model_used = self.model_tag
        response.reason = f"{self.capability.value} local model not configured; deterministic fallback active"
        return response
