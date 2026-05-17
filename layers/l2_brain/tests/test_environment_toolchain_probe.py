import os
import json
from pathlib import Path
from layers.l2_brain.environment_toolchain_probe import run_environment_toolchain_probe

def test_environment_toolchain_probe_execution(tmp_path):
    # Execute the probe
    res = run_environment_toolchain_probe(aiwg_root=str(tmp_path))
    
    assert "decision" in res
    assert "python" in res
    assert "go" in res
    assert "rust" in res
    assert "elixir" in res
    assert "node" in res
    
    # Assert JSON file was written correctly
    latest_json = tmp_path.joinpath(".aiwg/reports/environment_toolchain_probe_latest.json")
    assert latest_json.exists()
