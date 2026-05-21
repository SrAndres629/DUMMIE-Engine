"""LRU cache for embedding vectors."""
import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Callable, Optional

logger = logging.getLogger("dummie.embedding_cache")

class EmbeddingCache:
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _hash_content(self, content):
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, content):
        key = self._hash_content(content)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["time"] < self._ttl:
                self._cache.move_to_end(key)
                self._hits += 1
                return entry["vector"]
            else:
                del self._cache[key]
        self._misses += 1
        return None

    def put(self, content, vector):
        key = self._hash_content(content)
        self._cache[key] = {"vector": vector, "time": time.time()}
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def get_or_compute(self, content, compute_fn):
        vector = self.get(content)
        if vector is not None: return vector
        vector = compute_fn(content)
        self.put(content, vector)
        return vector

    @property
    def stats(self):
        total = self._hits + self._misses
        return {"size": len(self._cache), "max_size": self._max_size, "hits": self._hits, "misses": self._misses, "hit_rate": round(self._hits / max(1, total), 4), "ttl_seconds": self._ttl}

    def clear(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0

_embedding_cache = None

def get_embedding_cache(max_size=1000, ttl_seconds=3600):
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(max_size=max_size, ttl_seconds=ttl_seconds)
    return _embedding_cache

def cached_generate_vector(content, hint=None):
    cache = get_embedding_cache()
    from layers.l2_brain.embedding_mesh.specialized_providers import generate_vector
    return cache.get_or_compute(content, lambda c: generate_vector(c, hint=hint))
