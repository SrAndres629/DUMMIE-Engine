from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class VaultEmbeddingIndex:
    """
    [L2_BRAIN] Deterministic embedding index for the knowledge vault.
    Initial version uses hash-based vectors to simulate embeddings.
    """
    def __init__(self, root: str | Path = ".aiwg/vault"):
        self.root = Path(root)
        self.index_path = self.root / "vault_embedding_index.json"

    def index_entry(self, entry: dict) -> dict:
        vid = entry.get("vault_id")
        chash = entry.get("content_hash")
        if not vid or not chash:
            raise ValueError("vault_id and content_hash are required for indexing")

        index = self._load_index()
        
        # Check if already indexed with same hash
        existing = index.get("entries", {}).get(vid)
        if existing and existing.get("content_hash") == chash:
            return existing

        # Generate fake embedding
        vector = self._generate_fake_vector(chash)
        
        indexed_entry = {
            "vault_id": vid,
            "content_hash": chash,
            "embedding_model": "deterministic-hash-v1",
            "vector": vector,
            "summary": entry.get("summary", ""),
            "created_at": _now()
        }
        
        index.setdefault("entries", {})[vid] = indexed_entry
        index["updated_at"] = _now()
        index["total_entries"] = len(index["entries"])
        
        self._save_index(index)
        return indexed_entry

    def search_similar(self, query: str, top_k: int = 5) -> list[dict]:
        index = self._load_index()
        query_vector = self._generate_fake_vector(query)
        
        results = []
        for vid, entry in index.get("entries", {}).items():
            score = self._cosine_similarity(query_vector, entry["vector"])
            results.append({"vault_id": vid, "score": score, "summary": entry["summary"]})
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _generate_fake_vector(self, text: str, dimensions: int = 8) -> list[float]:
        """
        Generates a deterministic vector based on text hash.
        """
        h = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(dimensions):
            # Take 4 bytes per dimension
            chunk = h[i*4 : (i+1)*4]
            if len(chunk) < 4:
                chunk = chunk + b"\x00" * (4 - len(chunk))
            val = int.from_bytes(chunk, "big") / (2**32 - 1)
            vector.append(val)
        return vector

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = sum(a * a for a in v1) ** 0.5
        magnitude2 = sum(b * b for b in v2) ** 0.5
        if not magnitude1 or not magnitude2:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def _load_index(self) -> dict:
        if not self.index_path.exists():
            return {"updated_at": _now(), "total_entries": 0, "entries": {}}
        try:
            with open(self.index_path, "r", encoding="utf-8") as h:
                return json.load(h)
        except Exception as e:
            logger.error(f"Failed to load vault embedding index: {e}")
            return {"updated_at": _now(), "total_entries": 0, "entries": {}}

    def _save_index(self, index: dict):
        self.root.mkdir(parents=True, exist_ok=True)
        tmp_path = self.index_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as h:
            json.dump(index, h, indent=2, sort_keys=True)
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        os.replace(tmp_path, self.index_path)
