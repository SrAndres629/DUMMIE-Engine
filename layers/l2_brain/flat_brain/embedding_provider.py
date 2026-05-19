import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger("brain.embeddings")

class EmbeddingProvider:
    """
    Proveedor de Embeddings basado en FastEmbed (Spec 2026).
    Implementa Lazy Loading para optimizar el uso de memoria.
    """
    _model = None

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            try:
                from fastembed import TextEmbedding
                logger.info("Initializing FastEmbed model (BAAI/bge-small-en-v1.5)...")
                # bge-small-en-v1.5 es ligero (384 dim, ~100MB) y potente.
                cls._model = TextEmbedding()
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Embedding Provider Error: {e}")
        return cls._model

    @classmethod
    def generate_vector(cls, text: str) -> List[float]:
        """Genera un vector denso para un texto dado."""
        if not text:
            return [0.0] * 384
        
        try:
            model = cls._get_model()
            # fastembed genera un iterador de embeddings
            embeddings = list(model.embed([text]))
            return embeddings[0].tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")

    @classmethod
    def similarity(cls, v1: List[float], v2: List[float]) -> float:
        """Calcula la similitud de coseno entre dos vectores."""
        a = np.array(v1)
        b = np.array(v2)
        if not np.any(a) or not np.any(b):
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
