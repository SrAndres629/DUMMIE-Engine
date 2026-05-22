import json
from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.routing.strategies.base import BaseRoutingStrategy


COT_PROMPT = """You are a routing agent. Think step by step:

1. What is the user trying to do?
2. Which domain does this belong to? (media_generation, vcs, workspace_io, infrastructure, knowledge, shell)
3. Which gateway handles this? (media:8081, code:8082, infra:8083, knowledge:8084, shell:8085)
4. How confident are you? (0.0-1.0)

Available gateway servers:
- media: muapi (image/video/audio generation), mcp-comfyui (local image gen), cloudflare (AI inference)
- code: github (version control), git (git operations), filesystem (file read/write)
- infra: docker (containers), vercel (deployments)
- knowledge: sqlite (database), sequentialthinking (reasoning)
- shell: shell (commands), mcp-bash (bash), browser-use (web automation)

Respond with valid JSON only:
{"domain": "...", "action": "...", "gateway": "...", "confidence": 0.0-1.0, "reasoning": "step-by-step reasoning"}
"""


class CoTReasoningStrategy(BaseRoutingStrategy):
    name = "cot_reasoning"

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
                {"role": "system", "content": COT_PROMPT},
                {"role": "user", "content": query},
            ]
            text = await self._adapter.generate(messages, temperature=0.2)
            cleaned = (
                text.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            data = json.loads(cleaned)
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
