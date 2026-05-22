from typing import Optional
from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.routing.strategies.base import BaseRoutingStrategy
from dummie_sdk.config import get_config


class EmbeddingMatchStrategy(BaseRoutingStrategy):
    name = "embedding_match"
    MODEL_ID = "BAAI/bge-small-en-v1.5"

    GATEWAY_DOMAINS = {
        "media_generation": [
            "generate image",
            "create video",
            "produce audio",
            "media",
            "imagen",
            "video",
            "audio",
        ],
        "vcs": ["git status", "commit", "branch", "repository", "version control"],
        "workspace_io": ["read file", "write file", "filesystem", "directory"],
        "infrastructure": ["docker", "deploy", "container", "infrastructure"],
        "knowledge": ["query", "database", "sql", "search", "memory", "knowledge"],
        "shell": ["terminal", "command", "execute", "bash", "shell"],
    }

    def __init__(self, registry=None):
        super().__init__(registry)
        self._embedding = None

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded(self.MODEL_ID)
        if not self._adapter:
            return RoutingResult(match=False, confidence=0.0, strategy=self.name)

        try:
            candidates = []
            for domain, examples in self.GATEWAY_DOMAINS.items():
                query_vec = self._adapter.embed([query])[0]
                for ex in examples:
                    ex_vec = self._adapter.embed([ex])[0]
                    sim = sum(a * b for a, b in zip(query_vec, ex_vec))
                    candidates.append((domain, sim))
            candidates.sort(key=lambda x: x[1], reverse=True)
            if candidates and candidates[0][1] > 0.35:
                domain = candidates[0][0]
                return RoutingResult(
                    match=True,
                    domain=domain,
                    gateway=self._domain_to_gateway(domain),
                    confidence=float(candidates[0][1]),
                    strategy=self.name,
                )
        except Exception:
            pass
        return RoutingResult(match=False, confidence=0.0, strategy=self.name)

    def _domain_to_gateway(self, domain: str) -> str:
        mapping = {
            "media_generation": "media",
            "vcs": "code",
            "workspace_io": "code",
            "infrastructure": "infra",
            "knowledge": "knowledge",
            "shell": "shell",
        }
        return mapping.get(domain, "")
