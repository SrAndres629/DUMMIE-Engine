import pytest
import os
from layers.l5_muscle.workstation_operator import WorkstationOperator

@pytest.mark.asyncio
async def test_workstation_operator_shell_real():
    # Usamos el directorio actual como root seguro para el test
    op = WorkstationOperator(workspace_root=".")
    res = await op.execute_action("shell_command", {"command": "echo 'SVRN_TEST'"})
    assert res["status"] == "SUCCESS"
    assert "SVRN_TEST" in res["stdout"]

@pytest.mark.asyncio
async def test_workstation_operator_write_file_real(tmp_path):
    op = WorkstationOperator(workspace_root=str(tmp_path))
    res = await op.execute_action("write_file", {"path": "test_svrn.txt", "content": "HEARTBEAT"})
    assert res["status"] == "SUCCESS"
    assert (tmp_path / "test_svrn.txt").read_text() == "HEARTBEAT"

@pytest.mark.asyncio
async def test_workstation_operator_snapshot(tmp_path):
    target = tmp_path / "data.txt"
    target.write_text("v1")
    op = WorkstationOperator(workspace_root=str(tmp_path))
    res = await op.execute_action("file_snapshot", {"path": "data.txt"})
    assert res["status"] == "SUCCESS"
    assert "snapshot_id" in res

@pytest.mark.asyncio
async def test_workstation_operator_veto_outside_zone(tmp_path):
    op = WorkstationOperator(workspace_root=str(tmp_path))
    # Intento de acceso fuera del root
    res = await op.execute_action("write_file", {"path": "../dangerous.txt", "content": "EVIL"})
    assert res["status"] == "ERROR"
    assert "SOVEREIGN_VETO" in res["message"]

@pytest.mark.asyncio
async def test_workstation_operator_invalid_action():
    op = WorkstationOperator(workspace_root=".")
    res = await op.execute_action("unknown_move", {})
    assert res["status"] == "ERROR"
    assert "not implemented" in res["message"]
