from typing import Any
import os
import sys

ROOT_DIR = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", ""))
L3_DIR = os.path.join(ROOT_DIR, "layers", "l3_shield")
if ROOT_DIR and L3_DIR not in sys.path:
    sys.path.append(L3_DIR)

from knowledge_adapters import ObsidianKnowledgeAdapter
from knowledge_policy import evaluate_knowledge_operation


class KnowledgeToolService:
    def __init__(self, proxy_manager: Any):
        self.proxy_manager = proxy_manager
        self.adapter = ObsidianKnowledgeAdapter(proxy_manager)

    async def search_context(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        artifacts = await self.adapter.search_context(query, limit=limit)
        return [artifact.__dict__ for artifact in artifacts]

    async def get_artifact(self, source_uri: str) -> dict[str, Any]:
        artifact = await self.adapter.get_artifact(source_uri)
        return artifact.__dict__

    async def ingest_artifact(self, source_uri: str, ingest_reason: str) -> dict[str, Any]:
        artifact = await self.adapter.get_artifact(source_uri)
        return {
            "provider": artifact.provider,
            "source_uri": artifact.source_uri,
            "payload_hash": artifact.payload_hash,
            "ingest_reason": ingest_reason,
            "conflict_status": "none",
        }

    async def export_decision_summary(
        self,
        decision_id: str,
        summary: str,
        rationale: str,
        target_file: str,
    ) -> dict[str, Any]:
        body = f"\n## Decision {decision_id}\n\n{summary}\n\n### Rationale\n\n{rationale}\n"
        return await self._append_wisdom(
            wrapper="knowledge_export_decision_summary",
            target_file=target_file,
            content=body,
            source_event_id=decision_id,
        )

    async def export_lesson(
        self,
        lesson_id: str,
        issue: str,
        correction: str,
        target_file: str,
    ) -> dict[str, Any]:
        body = f"\n## Lesson {lesson_id}\n\nIssue: {issue}\n\nCorrection: {correction}\n"
        return await self._append_wisdom(
            wrapper="knowledge_export_lesson",
            target_file=target_file,
            content=body,
            source_event_id=lesson_id,
        )

    async def export_session_summary(
        self,
        session_id: str,
        summary: str,
        target_file: str,
    ) -> dict[str, Any]:
        body = f"\n## Session {session_id}\n\n{summary}\n"
        return await self._append_wisdom(
            wrapper="knowledge_export_session_summary",
            target_file=target_file,
            content=body,
            source_event_id=session_id,
        )

    async def _append_wisdom(
        self,
        wrapper: str,
        target_file: str,
        content: str,
        source_event_id: str,
    ) -> dict[str, Any]:
        policy = evaluate_knowledge_operation("obsidian_append_content", wrapper=wrapper)
        if policy.decision != "L3_AUTO_APPEND":
            return {"policy": policy.decision, "reason": policy.reason}
        await self.proxy_manager.call_tool(
            "obsidian",
            "obsidian_append_content",
            {"filepath": target_file, "content": content},
        )
        return {
            "provider": "obsidian",
            "filepath": target_file,
            "operation": "append",
            "policy": policy.decision,
            "source_event_id": source_event_id,
        }


def register_knowledge_tools(mcp, use_cases):
    service = KnowledgeToolService(use_cases.proxy_manager)

    @mcp.tool()
    async def knowledge_search_context(query: str, limit: int = 10) -> str:
        return str(await service.search_context(query, limit))

    @mcp.tool()
    async def knowledge_get_artifact(source_uri: str) -> str:
        return str(await service.get_artifact(source_uri))

    @mcp.tool()
    async def knowledge_ingest_artifact(source_uri: str, ingest_reason: str) -> str:
        return str(await service.ingest_artifact(source_uri, ingest_reason))

    @mcp.tool()
    async def knowledge_export_decision_summary(
        decision_id: str,
        summary: str,
        rationale: str,
        target_file: str,
    ) -> str:
        return str(await service.export_decision_summary(decision_id, summary, rationale, target_file))

    @mcp.tool()
    async def knowledge_export_lesson(
        lesson_id: str,
        issue: str,
        correction: str,
        target_file: str,
    ) -> str:
        return str(await service.export_lesson(lesson_id, issue, correction, target_file))

    @mcp.tool()
    async def knowledge_export_session_summary(
        session_id: str,
        summary: str,
        target_file: str,
    ) -> str:
        return str(await service.export_session_summary(session_id, summary, target_file))
