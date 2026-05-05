import json
from pathlib import Path

import pytest

from tools_impl.self_worktree import SelfWorktreeToolService


@pytest.mark.asyncio
async def test_self_session_start_creates_plan_only_session(tmp_path: Path):
    service = SelfWorktreeToolService(tmp_path)

    payload = await service.start("session-1", "Improve repo memory")

    assert payload["state"]["patch_application_enabled"] is False
    assert "intake.md" in payload["artifacts"]


@pytest.mark.asyncio
async def test_self_session_status_is_json_serializable(tmp_path: Path):
    service = SelfWorktreeToolService(tmp_path)
    await service.start("session-1", "Improve repo memory")

    payload = await service.status("session-1")

    json.dumps(payload)
    assert payload["session_id"] == "session-1"


@pytest.mark.asyncio
async def test_self_plan_next_loop_rejects_blocked_paths(tmp_path: Path):
    service = SelfWorktreeToolService(tmp_path)
    await service.start("session-1", "Improve repo memory")

    with pytest.raises(ValueError):
        await service.plan_next_loop("session-1", "Edit env", [".env"])


@pytest.mark.asyncio
async def test_self_plan_next_loop_returns_plan_and_next_loop(tmp_path: Path):
    service = SelfWorktreeToolService(tmp_path)
    await service.start("session-1", "Improve repo memory")

    payload = await service.plan_next_loop("session-1", "Improve docs", ["doc/CORE_SPEC.md"])

    assert payload["plan"]["apply_patch_enabled"] is False
    assert payload["next_loop"]["artifact"] == "next_loop.md"
