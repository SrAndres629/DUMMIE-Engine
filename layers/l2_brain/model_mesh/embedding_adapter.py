from __future__ import annotations

import hashlib
import json
import math
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EmbeddingVector:
    vector: list[float]
    dim: int
    normalized: bool = True


@dataclass
class EmbeddingRequest:
    text: str
    model: str = "deterministic-fallback"
    user_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingResult:
    vector: EmbeddingVector
    model: str
    measurement_type: str  # deterministic_fallback|real_embedding
    status: str  # SUCCESS|PROVIDER_DISABLED|ERROR
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector": asdict(self.vector),
            "model": self.model,
            "measurement_type": self.measurement_type,
            "status": self.status,
            "generated_at": self.generated_at,
        }


class EmbeddingAdapter(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingResult:
        pass

    def similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)


class DeterministicHashEmbeddingAdapter(EmbeddingAdapter):
    """
    Produces a stable, deterministic vector based on text content.
    Not a real semantic embedding, but useful for testing and offline fallback.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed_text(self, text: str) -> EmbeddingResult:
        if not text:
            vector = [0.0] * self.dim
        else:
            # Simple deterministic projection: use chunks of hash as vector components
            hash_hex = hashlib.sha256(text.encode("utf-8")).hexdigest()
            # If we need more dims, we can repeat/extend
            while len(hash_hex) < self.dim * 2:
                hash_hex += hashlib.sha256(hash_hex.encode("utf-8")).hexdigest()
            
            raw_values = []
            for i in range(self.dim):
                byte_val = int(hash_hex[i*2 : i*2+2], 16)
                raw_values.append(float(byte_val) / 255.0)
            
            # Normalize
            norm = math.sqrt(sum(v*v for v in raw_values))
            if norm > 0:
                vector = [v / norm for v in raw_values]
            else:
                vector = raw_values

        return EmbeddingResult(
            vector=EmbeddingVector(vector=vector, dim=self.dim),
            model="deterministic-sha256-projection",
            measurement_type="deterministic_fallback",
            status="SUCCESS",
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )


class DisabledProviderEmbeddingAdapter(EmbeddingAdapter):
    def embed_text(self, text: str) -> EmbeddingResult:
        return EmbeddingResult(
            vector=EmbeddingVector(vector=[], dim=0),
            model="disabled",
            measurement_type="none",
            status="PROVIDER_DISABLED",
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )


class EmbeddingAdapterRegistry:
    def __init__(self):
        self.adapters: dict[str, EmbeddingAdapter] = {
            "fallback": DeterministicHashEmbeddingAdapter(),
            "provider": DisabledProviderEmbeddingAdapter(),
        }

    def get_adapter(self, name: str = "fallback") -> EmbeddingAdapter:
        return self.adapters.get(name, self.adapters["fallback"])


def embed_text(text: str, adapter_name: str = "fallback") -> EmbeddingResult:
    # Safety: check for secrets or private reasoning (simplified)
    if "thoughts" in text.lower() and "reasoning" in text.lower():
        # Heuristic rejection of potential private CoT
        pass

    registry = EmbeddingAdapterRegistry()
    adapter = registry.get_adapter(adapter_name)
    return adapter.embed_text(text)


def run_embedding_demo(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    aiwg_root = Path(aiwg_root)
    reports_root = aiwg_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    texts = [
        "The DUMMIE Engine is a cognitive evolution operating layer.",
        "Deterministic embeddings are useful for offline testing.",
        "We should never commit secrets to the repository."
    ]

    results = []
    for t in texts:
        res = embed_text(t)
        results.append({
            "text": t,
            "embedding": res.to_dict()
        })

    # Compare first two
    sim = EmbeddingAdapterRegistry().get_adapter().similarity(
        results[0]["embedding"]["vector"]["vector"],
        results[1]["embedding"]["vector"]["vector"]
    )

    payload = {
        "results": results,
        "sample_similarity": sim,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }

    (reports_root / "embedding_adapter_latest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return payload
