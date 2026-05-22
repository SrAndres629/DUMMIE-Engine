import json
from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.routing.strategies.base import BaseRoutingStrategy


GATEWAYS_INFO = """
GATEWAYS:
- media (port 8081): muapi, mcp-comfyui, cloudflare
- code (port 8082): github, git, filesystem
- infra (port 8083): docker, vercel
- knowledge (port 8084): sqlite, sequentialthinking
- shell (port 8085): shell, mcp-bash, browser-use
"""


class LLMReasoningStrategy(BaseRoutingStrategy):
    name = "llm_reasoning"

    def __init__(self, registry=None, model_id: str = ""):
        super().__init__(registry)
        self.model_id = model_id

    async def execute(self, query: str) -> RoutingResult:
        cfg_model = self.model_id or ""
        if not cfg_model:
            from dummie_sdk.config import get_config

            cfg_model = get_config().default_model("llm") or "gemma4:2b"
        await self._ensure_loaded(cfg_model)
        if not self._adapter:
            return RoutingResult(match=False, confidence=0.0, strategy=self.name)

        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a routing engine. Given a user query, decide which gateway handles it.
{GATEWAYS_INFO}
Respond with JSON: {{"domain": "...", "action": "...", "gateway": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
Only use domains: media_generation, vcs, workspace_io, infrastructure, knowledge, shell.""",
                },
                {"role": "user", "content": query},
            ]
            text = await self._adapter.generate(messages, temperature=0.1)
            data = json.loads(
                text.strip().removeprefix("```json").removesuffix("```").strip()
            )
            return RoutingResult(
                match=data.get("confidence", 0) > 0.3,
                domain=data.get("domain", ""),
                action=data.get("action", ""),
                gateway=data.get("gateway", ""),
                confidence=float(data.get("confidence", 0)),
                strategy=self.name,
            )
        except Exception:
            pass
        return RoutingResult(match=False, confidence=0.0, strategy=self.name)
