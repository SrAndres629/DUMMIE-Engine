from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SelfWorktreeToolService:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir).resolve()
        try:
            from layers.l2_brain.self_worktree_orchestrator import SelfWorktreeOrchestrator
        except ImportError:
            from self_worktree_orchestrator import SelfWorktreeOrchestrator

        self.orchestrator = SelfWorktreeOrchestrator(self.root_dir)

    async def start(self, session_id: str, prompt: str = "") -> dict[str, Any]:
        session = self.orchestrator.start_self_session(session_id, prompt)
        self.orchestrator.load_global_context(session_id)
        self.orchestrator.assess_repo(session_id)
        return self.orchestrator.store.load_session(session_id)

    async def status(self, session_id: str) -> dict[str, Any]:
        return self.orchestrator.store.load_session(session_id)

    async def plan_next_loop(
        self,
        session_id: str,
        goal: str,
        candidate_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        plan = self.orchestrator.plan_safe_patch(session_id, goal, candidate_paths or [])
        next_loop = self.orchestrator.propose_next_loop(session_id)
        return {"plan": plan, "next_loop": next_loop}


def register_self_worktree_tools(mcp, root_dir: str):
    service = SelfWorktreeToolService(root_dir)

    @mcp.tool()
    async def dummie_self_session_start(session_id: str, prompt: str = "") -> str:
        """Start a plan-only self-evolution session. Does not apply patches."""
        return json.dumps(await service.start(session_id, prompt), indent=2, sort_keys=True)

    @mcp.tool()
    async def dummie_self_session_status(session_id: str) -> str:
        """Return status, events, and artifacts for a self-evolution session."""
        return json.dumps(await service.status(session_id), indent=2, sort_keys=True)

    @mcp.tool()
    async def dummie_self_plan_next_loop(
        session_id: str,
        goal: str,
        candidate_paths: list[str] | None = None,
    ) -> str:
        """Plan the next self-evolution loop without applying patches."""
        return json.dumps(
            await service.plan_next_loop(session_id, goal, candidate_paths or []),
            indent=2,
            sort_keys=True,
        )
