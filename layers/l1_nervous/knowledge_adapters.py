import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from models import SourceArtifact


class ObsidianKnowledgeAdapter:
    def __init__(self, proxy_manager: Any, server_name: str = "obsidian"):
        self.proxy_manager = proxy_manager
        self.server_name = server_name

    async def search_context(
        self,
        query: str,
        limit: int = 10,
        context_length: int = 200,
    ) -> list[SourceArtifact]:
        response = await self.proxy_manager.call_tool(
            self.server_name,
            "obsidian_simple_search",
            {"query": query, "context_length": context_length},
        )
        raw_text = self._extract_text(response)
        rows = json.loads(raw_text) if raw_text else []
        artifacts: list[SourceArtifact] = []
        for row in rows[:limit]:
            path = row.get("filename", "")
            matches = row.get("matches", [])
            excerpt = matches[0].get("context", "") if matches else ""
            artifacts.append(self._artifact(path, excerpt, {"score": row.get("score")}))
        return artifacts

    async def get_artifact(self, source_uri: str) -> SourceArtifact:
        filepath = self._source_uri_to_path(source_uri)
        response = await self.proxy_manager.call_tool(
            self.server_name,
            "obsidian_get_file_contents",
            {"filepath": filepath},
        )
        return self._artifact(filepath, self._extract_text(response), {})

    def _artifact(self, path: str, content: str, metadata: dict[str, Any]) -> SourceArtifact:
        payload_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return SourceArtifact(
            provider="obsidian",
            source_uri=f"obsidian://{path}",
            content_type="text/markdown",
            content=content,
            payload_hash=payload_hash,
            observed_at=datetime.now(timezone.utc).isoformat(),
            metadata={"path": path, **metadata},
        )

    def _extract_text(self, response: dict[str, Any]) -> str:
        content = response.get("result", {}).get("content", [])
        return "\n".join(item.get("text", "") for item in content if item.get("type") == "text")

    def _source_uri_to_path(self, source_uri: str) -> str:
        return source_uri.removeprefix("obsidian://")
