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
