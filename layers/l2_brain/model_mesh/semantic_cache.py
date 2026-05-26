import hashlib
import logging
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("brain.cache")


class SemanticCache:
    """
    L2_BRAIN Token optimization layer. Two-tier cache:
    1. Local in-memory: exact-match via SHA256 hash (fastest)
    2. Semantic: cosine similarity via EmbeddingProvider (real semantic matching)
    3. 4D-TES persistent: Kuzu stored node for cross-session durability
    """

    SEMANTIC_SIMILARITY_THRESHOLD = 0.92
    MAX_LOCAL_ENTRIES = 200
    TTL_SECONDS = 3600

    def __init__(self, kuzu_repo: Any = None):
        self.kuzu_repo = kuzu_repo
        self._local_memory: Dict[str, dict] = {}
        self._vector_memory: Dict[str, dict] = {}

    def _generate_hash(self, prompt: str, system_prompt: str) -> str:
        content = f"S:{system_prompt}|P:{prompt}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _get_embedding(self, text: str) -> List[float]:
        try:
            from layers.l2_brain.model_mesh.embedding_provider import EmbeddingProvider
        except ImportError:
            try:
                from layers.l2_brain.embedding_provider import EmbeddingProvider
            except ImportError:
                return []
        try:
            return EmbeddingProvider.generate_vector(text)
        except Exception as e:
            logger.debug(f"Embedding generation failed for cache: {e}")
            return []

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2:
            return 0.0
        try:
            import numpy as np

            a, b = np.array(v1), np.array(v2)
            if not np.any(a) or not np.any(b):
                return 0.0
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except Exception:
            return 0.0

    async def get(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        h = self._generate_hash(prompt, system_prompt)

        entry = self._local_memory.get(h)
        if entry and self._is_fresh(entry):
            logger.info(f"Cache HIT (Exact): {h[:12]}")
            return entry["response"]

        query_vec = self._get_embedding(prompt)
        if query_vec:
            best_score = 0.0
            best_response = None
            for cached_hash, cached in self._vector_memory.items():
                if not self._is_fresh(cached):
                    continue
                score = self._cosine_similarity(query_vec, cached.get("vector", []))
                if score > best_score and score >= self.SEMANTIC_SIMILARITY_THRESHOLD:
                    best_score = score
                    best_response = cached.get("response")
            if best_response:
                logger.info(f"Cache HIT (Semantic): score={best_score:.4f}")
                return best_response

        if self.kuzu_repo:
            try:
                nodes = self.kuzu_repo.semantic_search(
                    query_vec or query_vec or [], top_k=3
                )
                for node in nodes:
                    if node.intent_i == "CACHED_RESPONSE":
                        return node.payload
            except Exception as e:
                logger.debug(f"Kuzu cache lookup: {e}")

        return None

    async def set(self, prompt: str, response: str, system_prompt: str = ""):
        h = self._generate_hash(prompt, system_prompt)
        vector = self._get_embedding(prompt)

        entry = {
            "response": response,
            "vector": vector,
            "timestamp": time.time(),
            "prompt_hash": h,
        }

        self._local_memory[h] = entry
        if vector:
            self._vector_memory[h] = entry

        if len(self._local_memory) > self.MAX_LOCAL_ENTRIES:
            oldest = sorted(
                self._local_memory.items(), key=lambda x: x[1].get("timestamp", 0)
            )[:10]
            for k, _ in oldest:
                self._local_memory.pop(k, None)
                self._vector_memory.pop(k, None)

        if self.kuzu_repo:
            try:
                from layers.l2_brain.l2_memory_models import MemoryNode4D

                mem_node = MemoryNode4D.from_intent_context(
                    payload=response,
                    locus_x="cache",
                    locus_y="L2_BRAIN",
                    locus_z="PERSISTENCE",
                    authority_a="SEMANTIC_CACHE",
                    intent_i="CACHED_RESPONSE",
                )
                self.kuzu_repo.create_memory_node(mem_node)
            except Exception as e:
                logger.debug(f"Kuzu cache persist: {e}")

    def _is_fresh(self, entry: dict) -> bool:
        return (time.time() - entry.get("timestamp", 0)) < self.TTL_SECONDS

    def invalidate(self, prompt: str, system_prompt: str = ""):
        h = self._generate_hash(prompt, system_prompt)
        self._local_memory.pop(h, None)
        self._vector_memory.pop(h, None)

    def stats(self) -> dict:
        return {
            "local_entries": len(self._local_memory),
            "vector_entries": len(self._vector_memory),
            "similarity_threshold": self.SEMANTIC_SIMILARITY_THRESHOLD,
            "ttl_seconds": self.TTL_SECONDS,
        }
