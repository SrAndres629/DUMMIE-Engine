import time
from collections import OrderedDict


class EmbeddingCache:
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        self._cache: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str):
        if key not in self._cache:
            return None
        expires, value = self._cache[key]
        if time.time() > expires:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value, ttl: float = None):
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = (time.time() + ttl, value)
        self._cache.move_to_end(key)
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self):
        self._cache.clear()
