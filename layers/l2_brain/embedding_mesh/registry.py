# Spec Reference: 192_embedding_mesh_foundation
import logging

from .contracts import EmbeddingCapability
from .providers import (
    DeterministicFallbackProvider,
    FastEmbedTextProvider,
    IEmbeddingProvider,
    LegacyEmbeddingProviderAdapter,
    PlaceholderCapabilityProvider,
)

logger = logging.getLogger("brain.embedding_mesh.registry")


class EmbeddingRegistry:
    """
    Embedding provider registry by capability.

    Declares minimal provider mesh without introducing heavyweight dependencies.
    """

    def __init__(self):
        self._providers: dict[EmbeddingCapability, IEmbeddingProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        self._providers[EmbeddingCapability.FALLBACK] = DeterministicFallbackProvider(dimensions=384)

        # Placeholder capabilities use deterministic fallback with honest degraded status.
        self._providers[EmbeddingCapability.TEXT_FIDELITY] = PlaceholderCapabilityProvider(
            capability=EmbeddingCapability.TEXT_FIDELITY,
            dimensions=384,
            model_tag="placeholder-bge-m3",
        )
        self._providers[EmbeddingCapability.CODE] = PlaceholderCapabilityProvider(
            capability=EmbeddingCapability.CODE,
            dimensions=384,
            model_tag="placeholder-code-embedding",
        )
        self._providers[EmbeddingCapability.MULTIMODAL] = PlaceholderCapabilityProvider(
            capability=EmbeddingCapability.MULTIMODAL,
            dimensions=384,
            model_tag="placeholder-multimodal-embedding",
        )
        self._providers[EmbeddingCapability.RERANKER] = PlaceholderCapabilityProvider(
            capability=EmbeddingCapability.RERANKER,
            dimensions=384,
            model_tag="placeholder-reranker-embedding",
        )

        # Prefer compatibility adapter first. If it fails at runtime it degrades deterministically.
        self._providers[EmbeddingCapability.TEXT_FAST] = LegacyEmbeddingProviderAdapter()

        # Optionally prefer native fastembed wrapper if library is available.
        try:
            import fastembed  # noqa: F401

            self._providers[EmbeddingCapability.TEXT_FAST] = FastEmbedTextProvider()
            logger.info("EmbeddingRegistry: TEXT_FAST uses FastEmbedTextProvider.")
        except Exception:
            logger.info("EmbeddingRegistry: fastembed unavailable, TEXT_FAST uses legacy adapter/fallback.")

    def get_provider(self, capability: EmbeddingCapability) -> IEmbeddingProvider:
        return self._providers.get(capability, self._providers[EmbeddingCapability.FALLBACK])
