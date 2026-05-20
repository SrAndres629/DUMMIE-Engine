from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable

logger = logging.getLogger("dummie.knowledge_ports")

REPO_ROOT = Path(__file__).resolve().parents[2]
AIWG_MEMORY = REPO_ROOT / ".aiwg" / "memory"


class SourceArtifact:
    def __init__(self, source_uri: str, content: str, metadata: dict | None = None):
        self.source_uri = source_uri
        self.content = content
        self.metadata = metadata or {}


class ConsensusDecision:
    def __init__(self, decision_id: str, title: str, body: str, author: str = "dummie"):
        self.decision_id = decision_id
        self.title = title
        self.body = body
        self.author = author
        self.timestamp = __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()


class IntentDraft:
    def __init__(self, intent_id: str, goal: str, payload: dict | None = None):
        self.intent_id = intent_id
        self.goal = goal
        self.payload = payload or {}
        self.timestamp = __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()


class MemoryTemperatureSignal:
    def __init__(self, memory_id: str, temperature: str, reason: str):
        self.memory_id = memory_id
        self.temperature = temperature
        self.reason = reason


class RehydrationManifest:
    def __init__(self, source: str, target: str, artifacts: list[str] | None = None):
        self.source = source
        self.target = target
        self.artifacts = artifacts or []


@runtime_checkable
class KnowledgeProvider(Protocol):
    async def search_context(self, query: str, limit: int = 10) -> list[SourceArtifact]:
        ...

    async def get_artifact(self, source_uri: str) -> SourceArtifact:
        ...


@runtime_checkable
class WisdomPublisher(Protocol):
    async def publish_decision(self, decision: ConsensusDecision) -> str:
        ...

    async def publish_lesson(self, issue: str, correction: str) -> str:
        ...

    async def publish_session_summary(self, session_id: str, summary: str) -> str:
        ...


@runtime_checkable
class EntropyGovernor(Protocol):
    def classify(self, signals: list[MemoryTemperatureSignal]):
        ...


@runtime_checkable
class RehydrationProvider(Protocol):
    def dry_run(self, manifest: RehydrationManifest, artifacts: list[SourceArtifact]):
        ...


@runtime_checkable
class PreflightPublisher(Protocol):
    async def publish_intent_draft(self, draft: IntentDraft) -> str:
        ...


class KnowledgeWriteBridge:
    """Concrete implementation of write operations for knowledge artifacts.
    
    Routes writes through a tiered strategy:
    1. Obsidian MCP (if available) for human-readable journal
    2. .aiwg/memory/ for machine-readable persistence
    3. 4D-TES (KuzuDB) for causal memory
    """

    def __init__(self, obsidian_available: bool = False, mcp_gateway: Any = None):
        self.obsidian_available = obsidian_available
        self.mcp_gateway = mcp_gateway
        os.makedirs(str(AIWG_MEMORY), exist_ok=True)

    async def write_note(self, vault: str, title: str, content: str) -> dict:
        """Write a note to the knowledge store. Tries Obsidian first, falls back to .aiwg/."""
        result = {"status": "saved", "target": None, "uri": None}

        if self.obsidian_available and self.mcp_gateway:
            try:
                resp = await self.mcp_gateway.call_tool("obsidian", "create_note", {
                    "vault": vault,
                    "title": title,
                    "content": content,
                })
                result["status"] = "published"
                result["target"] = "obsidian"
                result["uri"] = resp
                logger.info(f"Published to Obsidian: {vault}/{title}")
                return result
            except Exception as e:
                logger.warning(f"Obsidian write failed, falling back: {e}")

        safe_title = title.replace(" ", "_").replace("/", "-")
        path = AIWG_MEMORY / f"{safe_title}.md"
        path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
        result["status"] = "saved"
        result["target"] = ".aiwg/memory"
        result["uri"] = str(path)
        logger.info(f"Saved to {path}")
        return result

    async def append_note(self, path: str, content: str) -> dict:
        """Append content to an existing note."""
        full_path = Path(path) if os.path.isabs(path) else AIWG_MEMORY / path
        if not full_path.exists():
            full_path.write_text(content, encoding="utf-8")
            return {"status": "created", "path": str(full_path)}
        existing = full_path.read_text(encoding="utf-8")
        full_path.write_text(existing + "\n" + content, encoding="utf-8")
        return {"status": "appended", "path": str(full_path)}

    async def write_session_summary(self, session_id: str, summary: str) -> dict:
        decision = ConsensusDecision(
            decision_id=f"sess-{session_id}",
            title=f"Session Summary: {session_id}",
            body=summary,
        )
        uri = await self._persist_decision(decision)
        return {"status": "written", "session_id": session_id, "uri": uri}

    async def write_lesson(self, issue: str, correction: str) -> dict:
        decision = ConsensusDecision(
            decision_id=f"lesson-{hash(issue)}",
            title=f"Lesson: {issue[:60]}",
            body=f"## Issue\n{issue}\n\n## Correction\n{correction}",
        )
        uri = await self._persist_decision(decision)
        return {"status": "written", "issue": issue, "uri": uri}

    async def publish_intent_draft(self, draft: IntentDraft) -> str:
        path = AIWG_MEMORY / f"intent_{draft.intent_id}.json"
        path.write_text(json.dumps({
            "intent_id": draft.intent_id,
            "goal": draft.goal,
            "payload": draft.payload,
            "timestamp": draft.timestamp,
        }, indent=2), encoding="utf-8")
        return str(path)

    async def _persist_decision(self, decision: ConsensusDecision) -> str:
        path = AIWG_MEMORY / f"decision_{decision.decision_id}.md"
        path.write_text(
            f"---\nid: {decision.decision_id}\nauthor: {decision.author}\n"
            f"timestamp: {decision.timestamp}\n---\n\n"
            f"# {decision.title}\n\n{decision.body}\n",
            encoding="utf-8",
        )
        return str(path)

    async def list_notes(self, prefix: str = "") -> list[dict]:
        notes = []
        for f in AIWG_MEMORY.glob(f"{prefix}*.md"):
            notes.append({
                "name": f.stem,
                "path": str(f),
                "size": f.stat().st_size,
                "modified": __import__("datetime").datetime.fromtimestamp(
                    f.stat().st_mtime
                ).isoformat(),
            })
        return notes
