import json
import time
import logging
from typing import Optional

logger = logging.getLogger("dummie-smart.smart-router")


DOMAIN_MAP = {
    "media_generation": {
        "gateway": "media",
        "port": 8081,
        "action": "generate",
        "servers": ["mcp-comfyui", "cloudflare"],
    },
    "vcs": {
        "gateway": "code",
        "port": 8082,
        "action": "git",
        "servers": ["github", "git"],
    },
    "workspace_io": {
        "gateway": "code",
        "port": 8082,
        "action": "file",
        "servers": ["filesystem"],
    },
    "infrastructure": {
        "gateway": "infra",
        "port": 8083,
        "action": "deploy",
        "servers": ["docker", "vercel"],
    },
    "knowledge": {
        "gateway": "knowledge",
        "port": 8084,
        "action": "query",
        "servers": ["sqlite", "sequentialthinking"],
    },
    "shell": {
        "gateway": "shell",
        "port": 8085,
        "action": "shell",
        "servers": ["shell", "mcp-bash", "browser-use"],
    },
}


SYSTEM_PROMPT = """You are a tool router for the DUMMIE Engine. Your job is to classify a user query into the correct domain and generate the ordered tool sequence to handle it.

Domains and their tools:
- media_generation: servers=[mcp-comfyui, cloudflare], for images, video, audio generation
- vcs: servers=[github, git], for git operations, branches, repos
- workspace_io: servers=[filesystem], for reading/writing files
- infrastructure: servers=[docker, vercel], for containers, deployments
- knowledge: servers=[sqlite, sequentialthinking], for queries, reasoning
- shell: servers=[shell, mcp-bash, browser-use], for terminal, browser

Respond ONLY with valid JSON:
{
  "domain": "one of the domain names above",
  "action": "brief action name",
  "tools": [{"server": "...", "tool": "...", "arguments": {}, "step_id": "1"}],
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation of why this routing was chosen"
}"""


class SmartRouter:
    """Two-stage router using Qwen3.5:0.8b with KV cache prefixing.

    Stage 1: Domain classification via short generation (~60-120ms with warm cache).
    Stage 2: Full tool sequence generation for verified queries (~200-500ms with warm cache).

    KV cache is warmed on first call (system prompt is pre-computed once).
    """

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "qwen3.5:0.8b",
        confidence_threshold: float = 0.6,
        fallback_model: str = "gemma4:e2b",
    ):
        self.ollama_host = ollama_host
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.fallback_model = fallback_model
        self._kv_warmed = False

    async def _ollama_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        num_predict: int = 150,
        temperature: float = 0.1,
    ) -> dict:
        import httpx

        body = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "num_predict": num_predict,
                "temperature": temperature,
            },
            "stream": False,
            "keep_alive": -1,
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.ollama_host}/api/generate",
                json=body,
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()

    async def warm_kv_cache(self):
        if self._kv_warmed:
            return
        logger.info("Warming KV cache for %s ...", self.model)
        try:
            await self._ollama_generate(
                prompt="warmup",
                system=SYSTEM_PROMPT,
                num_predict=1,
            )
            self._kv_warmed = True
            logger.info("KV cache warmed successfully")
        except Exception as e:
            logger.warning("KV cache warmup failed: %s (will retry on first call)", e)

    async def route(self, query: str, tools_available: Optional[dict] = None) -> dict:
        if not query or not query.strip():
            return self._empty_result(query, error="Empty query")
        t0 = time.time()
        if not self._kv_warmed:
            await self.warm_kv_cache()

        user_prompt = f"User query: {query}\n\nJSON:"
        try:
            resp = await self._ollama_generate(
                prompt=user_prompt,
                system=SYSTEM_PROMPT,
                num_predict=200,
            )
        except Exception as e:
            logger.error("Router generation failed: %s", e)
            return self._empty_result(query, error=str(e))

        raw_output = resp.get("response", "")
        elapsed = (time.time() - t0) * 1000

        parsed = self._parse_json(raw_output)
        if parsed is None:
            logger.warning("Failed to parse router output: %.100s", raw_output)
            return self._empty_result(query, error="Failed to parse router output")

        domain = parsed.get("domain", "")
        confidence = float(parsed.get("confidence", 0.0))
        action = parsed.get("action", "")
        tools = parsed.get("tools", [])

        if domain not in DOMAIN_MAP:
            logger.warning("Unknown domain from router: %s", domain)
            return self._empty_result(
                query, error=f"Unknown domain: {domain}", confidence=confidence
            )

        if confidence < self.confidence_threshold:
            logger.info(
                "Low confidence (%.2f < %.2f), triggering fallback embedding",
                confidence,
                self.confidence_threshold,
            )
            fallback = await self._embedding_fallback(query, domain, confidence)
            if fallback:
                return fallback

        gw = DOMAIN_MAP[domain]
        result = {
            "match": True,
            "domain": domain,
            "action": action or gw["action"],
            "gateway": gw["gateway"],
            "port": gw["port"],
            "confidence": round(confidence, 4),
            "strategy": "smart_router",
            "latency_ms": round(elapsed, 1),
            "servers": gw["servers"],
            "tools": tools,
            "query": query,
        }
        if tools:
            result["tool_count"] = len(tools)

        logger.debug(
            "Routed '%s' -> %s (conf=%.2f, %.0fms)",
            query[:60],
            domain,
            confidence,
            elapsed,
        )
        return result

    async def _embedding_fallback(
        self, query: str, hint_domain: str, hint_confidence: float
    ) -> Optional[dict]:
        try:
            from dummie_sdk.routing.strategies.embedding_match import (
                EmbeddingMatchStrategy,
            )
        except ImportError:
            return None

        import sys

        for attempt in range(2):
            try:
                if attempt == 0:
                    strat = EmbeddingMatchStrategy()
                else:
                    from dummie_sdk.models.model_registry import ModelRegistry

                    strat = EmbeddingMatchStrategy(registry=ModelRegistry())
                result = await strat.execute(query)
            except Exception as e:
                logger.warning("Embedding fallback attempt %d failed: %s", attempt, e)
                continue

            if result.match and result.confidence >= 0.3:
                gw = DOMAIN_MAP.get(result.domain)
                if not gw:
                    continue
                return {
                    "match": True,
                    "domain": result.domain,
                    "action": result.action or "",
                    "gateway": gw["gateway"],
                    "port": gw["port"],
                    "confidence": round(max(hint_confidence, result.confidence), 4),
                    "strategy": "embedding_fallback",
                    "latency_ms": result.latency_ms,
                    "servers": gw["servers"],
                    "query": query,
                }
        return None

    def _parse_json(self, raw: str) -> Optional[dict]:
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            cleaned = []
            in_code = False
            for line in lines:
                if line.startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    cleaned.append(line)
            raw = "\n".join(cleaned).strip()
        brace = raw.find("{")
        if brace >= 0:
            raw = raw[brace:]
        end = raw.rfind("}")
        if end >= 0:
            raw = raw[: end + 1]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _empty_result(
        self, query: str, error: str = "", confidence: float = 0.0
    ) -> dict:
        return {
            "match": False,
            "domain": None,
            "confidence": confidence,
            "message": error,
            "query": query,
            "strategy": "smart_router",
            "latency_ms": 0.0,
        }
