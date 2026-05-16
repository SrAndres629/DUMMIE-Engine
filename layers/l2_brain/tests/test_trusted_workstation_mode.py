import json
import pytest
from pathlib import Path
from layers.l2_brain.trusted_workstation_mode import TrustedWorkstationMode, WorkstationAction

@pytest.fixture
def tw_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    return aiwg

def test_tw_allows_read_only(tw_env):
    mode = TrustedWorkstationMode(aiwg_root=tw_env)
    res = mode.evaluate_action(WorkstationAction("a1", "READ_ONLY_STATUS", "git status"))
    assert res.decision == "ALLOW"
    assert res.can_execute_now == True

def test_tw_blocks_env_access(tw_env):
    mode = TrustedWorkstationMode(aiwg_root=tw_env)
    res = mode.evaluate_action(WorkstationAction("a2", "ENV_ACCESS", "read .env", target_paths=[".env"]))
    assert res.decision == "BLOCK"
    assert "strictly forbidden" in res.reason or "sensitive" in res.reason

def test_tw_requires_auth_for_mutation(tw_env):
    mode = TrustedWorkstationMode(aiwg_root=tw_env)
    res = mode.evaluate_action(WorkstationAction("a3", "WORKSPACE_EDIT", "write", requires_workspace_mutation=True))
    assert res.decision == "ALLOW_WITH_HUMAN_APPROVAL"
    assert res.requires_authorization == True

def test_tw_denies_browser(tw_env):
    mode = TrustedWorkstationMode(aiwg_root=tw_env)
    res = mode.evaluate_action(WorkstationAction("a4", "BROWSER_CONTROL", "open"))
    assert res.decision == "BLOCK"
