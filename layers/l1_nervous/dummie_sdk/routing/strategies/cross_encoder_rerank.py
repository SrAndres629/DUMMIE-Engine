from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.routing.strategies.base import BaseRoutingStrategy


class CrossEncoderRerankStrategy(BaseRoutingStrategy):
    name = "cross_encoder_rerank"
    MODEL_ID = "cross-encoder/ms-marco-MiniLM-L-2-v2"

    DOMAIN_CANDIDATES = [
        "media_generation",
        "vcs",
        "workspace_io",
        "infrastructure",
        "knowledge",
        "shell",
    ]
    DOMAIN_DESCRIPTIONS = {
        "media_generation": "Create, edit, or generate images, videos, audio",
        "vcs": "Git operations, version control, branches, commits",
        "workspace_io": "Read and write files, filesystem operations",
        "infrastructure": "Docker, deploy, cloud infrastructure management",
        "knowledge": "Database queries, memory, search, reasoning",
        "shell": "Command execution, terminal, browser automation",
    }

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded(self.MODEL_ID)
        if not self._adapter:
            return RoutingResult(match=False, confidence=0.0, strategy=self.name)

        try:
            candidates = [self.DOMAIN_DESCRIPTIONS[d] for d in self.DOMAIN_CANDIDATES]
            scored = self._adapter.rerank(query, candidates)
            if scored:
                best_desc, score = scored[0]
                idx = candidates.index(best_desc)
                domain = self.DOMAIN_CANDIDATES[idx]
                return RoutingResult(
                    match=True,
                    domain=domain,
                    gateway=self._domain_to_gateway(domain),
                    confidence=float(score),
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
