import pytest
from layers.l5_muscle.workstation_operator import WorkstationOperator

@pytest.mark.asyncio
async def test_workstation_operator_shell_simulated():
    op = WorkstationOperator(workspace_root="/tmp")
    res = await op.execute_action("shell_command", {"command": "ls -la"})
    assert res["status"] == "SUCCESS"
    assert "Executed" in res["output"]

@pytest.mark.asyncio
async def test_workstation_operator_snapshot():
    op = WorkstationOperator(workspace_root="/tmp")
    res = await op.execute_action("file_snapshot", {"path": "test.txt"})
    assert res["status"] == "SUCCESS"
    assert "snapshot_id" in res

@pytest.mark.asyncio
async def test_workstation_operator_invalid_action():
    op = WorkstationOperator(workspace_root="/tmp")
    res = await op.execute_action("invalid", {})
    assert res["status"] == "ERROR"


@pytest.mark.asyncio
async def test_workstation_operator_requires_approval_for_external_authority(tmp_path):
    op = WorkstationOperator(workspace_root=str(tmp_path))

    res = await op.execute_action(
        "shell_command",
        {"command": "echo hi", "authority_level": "A4_EXTERNAL_ACTOR"},
    )

    assert res["status"] == "BLOCKED"
    assert res["requires_approval"] is True


@pytest.mark.asyncio
async def test_workstation_operator_creates_real_checkpoint_inside_safe_zone(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("before", encoding="utf-8")
    op = WorkstationOperator(workspace_root=str(tmp_path))

    res = await op.execute_action("file_snapshot", {"path": "notes.txt", "authority_level": "A2_BUILDER"})

    assert res["status"] == "SUCCESS"
    assert res["snapshot_id"] != "snap_12345"
    assert (tmp_path / ".aiwg" / "checkpoints" / res["snapshot_id"] / "notes.txt").exists()


@pytest.mark.asyncio
async def test_workstation_operator_blocks_paths_outside_safe_zone(tmp_path):
    op = WorkstationOperator(workspace_root=str(tmp_path))

    res = await op.execute_action("file_snapshot", {"path": "../outside.txt"})

    assert res["status"] == "ERROR"
    assert "safe zone" in res["message"].lower()
