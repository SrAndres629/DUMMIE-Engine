import json
import pytest
from pathlib import Path
from layers.l2_brain.context_enforcement_gate import ContextEnforcementGate

@pytest.fixture
def gate_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    (aiwg / "reports").mkdir(parents=True)
    
    manifest = {"repo_id": "test", "tracked_files_count": 10}
    (intel / "repo_intelligence_manifest.json").write_text(json.dumps(manifest))
    return aiwg

def test_gate_blocks_bulk_load(gate_env):
    gate = ContextEnforcementGate(aiwg_root=gate_env)
    req = {"task_type": "analysis", "requires_full_repo_scan": True}
    res = gate.evaluate_context_request(req)
    assert res.decision == "BLOCK_RAW_FOLDER_BULK_LOAD"

def test_gate_allows_dossier_context(gate_env):
    gate = ContextEnforcementGate(aiwg_root=gate_env)
    req = {"task_type": "analysis", "requires_code_read": False}
    res = gate.evaluate_context_request(req)
    assert res.decision == "ALLOW_DOSSIER_CONTEXT"

def test_gate_allows_file_read(gate_env):
    gate = ContextEnforcementGate(aiwg_root=gate_env)
    req = {"task_type": "debugging", "requires_code_read": True}
    res = gate.evaluate_context_request(req)
    assert res.decision == "ALLOW_SELECTED_FILE_READ"
