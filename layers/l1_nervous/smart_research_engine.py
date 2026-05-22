import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError

logger = logging.getLogger("dummie-mcp.research-engine")

GITHUB_TOKEN = os.environ.get(
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    os.environ.get("GITHUB_TOKEN", ""),
)

RESEARCH_INDEX = {
    "video.generation": {
        "github_query": "topic:mcp-server+videogeneration+stars:>50",
        "keywords": ["mcp-server video", "video generation", "text-to-video"],
        "known": [
            {"name": "ComfyUI-MCP", "url": "github.com/ComfyUI-MCP"},
            {"name": "video-crafter", "url": "github.com/VideoCrafter"},
            {"name": "animate-diff-mcp", "url": "github.com/animatediff-mcp"},
        ],
    },
    "audio.generation": {
        "github_query": "topic:mcp-server+audiogeneration+stars:>50",
        "keywords": ["audio generation", "music generation", "tts"],
        "known": [
            {"name": "bark-mcp", "url": "github.com/bark-mcp"},
            {"name": "audiocraft-mcp", "url": "github.com/audiocraft"},
        ],
    },
    "image.edit": {
        "github_query": "topic:mcp-server+imageedit+inpainting+stars:>50",
        "keywords": ["image editing", "inpainting", "outpainting"],
        "known": [],
    },
    "code.test": {
        "github_query": "topic:mcp-server+testing+stars:>50",
        "keywords": ["testing", "test generation", "unit test"],
        "known": [],
    },
    "code.analyze": {
        "github_query": "topic:mcp-server+codeanalysis+stars:>50",
        "keywords": ["code analysis", "linting", "static analysis"],
        "known": [],
    },
    "memory.search": {
        "github_query": "topic:mcp-server+memory+rag+stars:>50",
        "keywords": ["memory", "RAG", "vector search"],
        "known": [],
    },
    "data.query": {
        "github_query": "topic:mcp-server+database+sql+stars:>50",
        "keywords": ["database", "SQL", "query"],
        "known": [],
    },
    "infrastructure.monitor": {
        "github_query": "topic:mcp-server+monitoring+stars:>50",
        "keywords": ["monitoring", "observability", "metrics"],
        "known": [],
    },
    "general": {
        "github_query": "topic:mcp-server+stars:>100",
        "keywords": [],
        "known": [],
    },
}


class SmartResearchEngine:
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_ttl = 3600

    def search(
        self, domain: str = "", action: str = "", query: str = ""
    ) -> Optional[dict]:
        key = f"{domain}.{action}" if domain and action else query.lower()

        if key in self._cache:
            elapsed = time.time() - self._cache[key].get("_cached_at", 0)
            if elapsed < self._cache_ttl:
                logger.debug("Research cache hit: %s", key)
                return self._cache[key]

        result = self._github_search(domain, action, query)

        if result:
            result["_cached_at"] = time.time()
            self._cache[key] = result

        return result

    def _github_search(self, domain: str, action: str, query: str) -> dict:
        research_key = f"{domain}.{action}" if domain and action else "general"
        spec = RESEARCH_INDEX.get(research_key) or RESEARCH_INDEX.get("general")

        tokens = self._extract_search_tokens(query, domain, action)
        gh_query = self._build_github_query(tokens, spec)
        results = self._call_github_api(gh_query)

        known = spec.get("known", [])
        for k in known:
            k["type"] = "known_repo"

        if results:
            for k in known:
                k["stars"] = k.get("stars", 0)
            all_results = known + results
            all_results.sort(key=lambda x: x.get("stars", 0), reverse=True)
        else:
            all_results = known

        return {
            "domain": domain,
            "action": action,
            "github_query": gh_query,
            "total_count": len(all_results),
            "results": all_results[:10],
            "cached": False,
        }

    def _extract_search_tokens(self, query: str, domain: str, action: str) -> list:
        tokens = []
        if domain:
            tokens.append(domain)
        if action:
            tokens.append(action)
        if query:
            for w in query.lower().split():
                if len(w) > 3 and w not in tokens:
                    tokens.append(w)
        return tokens[:5]

    def _build_github_query(self, tokens: list, spec: dict) -> str:
        base = spec.get("github_query", "topic:mcp-server+stars:>50")

        extra_terms = "+".join(tokens[:3])
        if extra_terms and extra_terms not in base:
            if extra_terms not in base:
                base = f"topic:mcp-server+{extra_terms}+stars:>50"

        return base

    def _call_github_api(self, query: str) -> list:
        encoded = query.replace("+", "%20").replace(":", "%3A").replace(">", "%3E")
        url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=10"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "DUMMIE-Research-Engine/1.0",
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

        try:
            req = Request(url, headers=headers, method="GET")
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                items = data.get("items", [])
                return [
                    {
                        "name": item.get("full_name", ""),
                        "url": item.get("html_url", ""),
                        "description": (item.get("description", "") or "")[:200],
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", "unknown"),
                        "updated_at": item.get("updated_at", ""),
                        "type": "github_result",
                    }
                    for item in items[:10]
                ]
        except HTTPError as e:
            if e.code == 403:
                logger.warning("GitHub API rate limit excedido")
                remaining = e.headers.get("X-RateLimit-Remaining", "?")
                reset = e.headers.get("X-RateLimit-Reset", "?")
                logger.warning(
                    "Rate limit: %s remaining, resets at %s",
                    remaining,
                    reset,
                )
            else:
                logger.warning("GitHub API error %s: %s", e.code, e.reason)
            return []
        except Exception as e:
            logger.warning("GitHub API exception: %s", e)
            return []
