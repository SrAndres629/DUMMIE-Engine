# Spec Reference: 192_embedding_mesh_foundation
import abc
from layers.l2_brain.domain.embedding_contract import (
    EmbeddingRequest,
    EmbeddingResponse,
    CompressionRequest,
    CompressionResponse,
)


class IEmbeddingAdapter(abc.ABC):
    """Puerto Hexagonal (Domain Port) para generación de Embeddings"""

    @abc.abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        pass


class IContextCompressor(abc.ABC):
    """Puerto Hexagonal (Domain Port) para Compresión de Contexto"""

    @abc.abstractmethod
    def compress(self, request: CompressionRequest) -> CompressionResponse:
        pass
