import time
import pickle
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger("dummie-smart.semantic-cache")


@dataclass
class CacheEntry:
    query: str
    embedding: np.ndarray
    route_result: dict
    timestamp: float = 0.0
    ttl: float = 300.0
    hit_count: int = 0
    last_accessed: float = 0.0


class SemanticRouteCache:
    """Two-layer semantic route cache.

    L1: exact hash match (O(1) dict lookup, ~30ns).
    L2: cosine similarity via batched numpy dot (~15μs for 1000 entries).

    Persistence via pickle dump/load.
    """

    def __init__(
        self,
        embedding_dim: int = 384,
        default_ttl: float = 300.0,
        similarity_threshold: float = 0.90,
        max_entries: int = 5000,
        ollama_host: str = "http://localhost:11434",
        embedding_model: str = "granite-embedding:30m",
    ):
        self.embedding_dim = embedding_dim
        self.default_ttl = default_ttl
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.ollama_host = ollama_host
        self.embedding_model = embedding_model

        self._l1: dict[str, int] = {}
        self._entries: list[CacheEntry] = []
        self._embeddings: np.ndarray = np.empty((0, embedding_dim), dtype=np.float32)
        self._lock = None

    async def _ensure_lock(self):
        if self._lock is None:
            import asyncio

            self._lock = asyncio.Lock()

    def _validate_embedding(self, emb: np.ndarray) -> bool:
        if emb.shape[0] != self.embedding_dim:
            logger.warning(
                "Embedding dim mismatch: got %d, expected %d",
                emb.shape[0],
                self.embedding_dim,
            )
            return False
        return True

    async def _embed(self, text: str) -> np.ndarray:
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.ollama_host}/api/embed",
                json={"model": self.embedding_model, "input": [text]},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
        emb = data["embeddings"][0]
        return np.array(emb, dtype=np.float32)

    def _is_fresh(self, entry: CacheEntry) -> bool:
        return (time.monotonic() - entry.timestamp) < entry.ttl

    def _hash(self, query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    async def get(self, query: str) -> Optional[dict]:
        await self._ensure_lock()
        async with self._lock:
            query_hash = self._hash(query)
            idx = self._l1.get(query_hash)
            if idx is not None and idx < len(self._entries):
                entry = self._entries[idx]
                if self._is_fresh(entry):
                    entry.hit_count += 1
                    entry.last_accessed = time.time()
                    logger.debug(
                        "L1 cache hit: query=%s (hits=%d)", query[:60], entry.hit_count
                    )
                    return entry.route_result

            if len(self._entries) == 0:
                return None

        query_emb = await self._embed(query)

        async with self._lock:
            scores = np.dot(self._embeddings, query_emb)
            best_idx = int(np.argmax(scores))
            if scores[best_idx] >= self.similarity_threshold:
                entry = self._entries[best_idx]
                if self._is_fresh(entry):
                    entry.hit_count += 1
                    entry.last_accessed = time.time()
                    logger.debug(
                        "L2 cache hit: query=%s sim=%.4f (hits=%d)",
                        query[:60],
                        float(scores[best_idx]),
                        entry.hit_count,
                    )
                    return entry.route_result

        return None

    async def set(self, query: str, route_result: dict):
        if self.max_entries == 0:
            logger.debug("Cache disabled (max_entries=0), skipping set")
            return
        if not query or not query.strip():
            return

        query_emb = await self._embed(query)
        if not self._validate_embedding(query_emb):
            return

        query_hash = self._hash(query)
        now = time.monotonic()

        await self._ensure_lock()
        async with self._lock:
            idx = self._l1.get(query_hash)
            if idx is not None and idx < len(self._entries):
                existing = self._entries[idx]
                existing.route_result = route_result
                existing.timestamp = now
                existing.embedding = query_emb
                self._embeddings[idx] = query_emb
                logger.debug("Cache update: query=%s", query[:60])
                return

            if len(self._entries) >= self.max_entries:
                await self._evict_one()

            entry = CacheEntry(
                query=query,
                embedding=query_emb,
                route_result=route_result,
                timestamp=now,
                ttl=self.default_ttl,
            )
            idx = len(self._entries)
            self._l1[query_hash] = idx
            self._entries.append(entry)
            self._embeddings = np.vstack([self._embeddings, query_emb[None, :]])
            logger.debug(
                "Cache set: query=%s (total=%d)", query[:60], len(self._entries)
            )

    async def _evict_one(self):
        lru_idx = min(
            range(len(self._entries)),
            key=lambda i: self._entries[i].last_accessed,
        )
        evicted = self._entries.pop(lru_idx)
        self._l1.pop(self._hash(evicted.query), None)
        self._embeddings = np.delete(self._embeddings, lru_idx, axis=0)
        for qh, idx in list(self._l1.items()):
            if idx > lru_idx:
                self._l1[qh] = idx - 1
        logger.debug(
            "Cache evict: %s (total=%d)", evicted.query[:60], len(self._entries)
        )

    async def get_stats(self) -> dict:
        total = len(self._entries)
        if total == 0:
            return {"total_entries": 0, "total_hits": 0}
        total_hits = sum(e.hit_count for e in self._entries)
        return {"total_entries": total, "total_hits": total_hits}

    async def save(self, path: str):
        data = {
            "l1": self._l1,
            "entries": [
                {
                    "query": e.query,
                    "embedding": e.embedding.tolist(),
                    "route_result": e.route_result,
                    "timestamp": e.timestamp,
                    "ttl": e.ttl,
                    "hit_count": e.hit_count,
                    "last_accessed": e.last_accessed,
                }
                for e in self._entries
            ],
            "embedding_dim": self.embedding_dim,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.debug("Cache saved: %d entries -> %s", len(self._entries), path)

    async def load(self, path: str):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError, EOFError, Exception) as e:
            logger.warning("Failed to load cache from %s: %s", path, e)
            return
        self._l1 = data.get("l1", {})
        entries_raw = data.get("entries", [])
        self._entries = [
            CacheEntry(
                query=e.get("query", ""),
                embedding=np.array(e.get("embedding", []), dtype=np.float32),
                route_result=e.get("route_result", {}),
                timestamp=e.get("timestamp", 0.0),
                ttl=e.get("ttl", self.default_ttl),
                hit_count=e.get("hit_count", 0),
                last_accessed=e.get("last_accessed", 0.0),
            )
            for e in entries_raw
        ]
        if self._entries:
            self._embeddings = np.array(
                [e.embedding for e in self._entries], dtype=np.float32
            )
        else:
            self._embeddings = np.empty((0, self.embedding_dim), dtype=np.float32)
        logger.debug("Cache loaded: %d entries from %s", len(self._entries), path)
