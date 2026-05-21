import pytest
import time
from layers.l2_brain.embedding_mesh.vector_cache import EmbeddingCache, get_embedding_cache


class TestEmbeddingCache:
    def test_cache_hit(self):
        cache = EmbeddingCache(max_size=10)
        cache.put("hello", [0.1, 0.2, 0.3])
        assert cache.get("hello") == [0.1, 0.2, 0.3]

    def test_cache_miss(self):
        cache = EmbeddingCache(max_size=10)
        assert cache.get("hello") is None

    def test_lru_eviction(self):
        cache = EmbeddingCache(max_size=2)
        cache.put("a", [1.0])
        cache.put("b", [2.0])
        cache.put("c", [3.0])
        assert cache.get("a") is None
        assert cache.get("b") == [2.0]
        assert cache.get("c") == [3.0]

    def test_stats(self):
        cache = EmbeddingCache(max_size=10)
        cache.put("a", [1.0])
        cache.get("a")
        cache.get("b")
        stats = cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_get_or_compute(self):
        cache = EmbeddingCache(max_size=10)
        compute_count = [0]
        def compute(content):
            compute_count[0] += 1
            return [float(ord(c)) for c in content[:3]]
        v1 = cache.get_or_compute("hello", compute)
        v2 = cache.get_or_compute("hello", compute)
        assert v1 == v2
        assert compute_count[0] == 1

    def test_clear(self):
        cache = EmbeddingCache(max_size=10)
        cache.put("a", [1.0])
        cache.clear()
        assert cache.get("a") is None

    def test_ttl_expiry(self):
        cache = EmbeddingCache(max_size=10, ttl_seconds=0)
        cache.put("a", [1.0])
        time.sleep(0.1)
        assert cache.get("a") is None

    def test_global_cache(self):
        cache1 = get_embedding_cache()
        cache2 = get_embedding_cache()
        assert cache1 is cache2
