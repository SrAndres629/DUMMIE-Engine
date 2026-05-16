import json
import pytest
from pathlib import Path
from layers.l2_brain.cli_control_plane import CliControlPlane
from layers.l2_brain.tui_process_monitor import TuiProcessMonitor
from layers.l6_skin.dashboard_renderer import DashboardRenderer

@pytest.fixture
def real_aiwg_setup(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    current = {"plan": "DUMMIE TEST", "current_phase": "P21"}
    seed = {"next_phase": "P22"}
    
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    # Mock restart gate to PASS
    (repo / "restart_integration_gate_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    return aiwg

def test_cli_status_coherence(real_aiwg_setup):
    plane = CliControlPlane(aiwg_root=real_aiwg_setup)
    result = plane.run_command("status")
    
    assert result.decision == "PASS_WITH_WARNINGS" # because many reports are missing
    assert result.payload["current_phase"] == "P21"
    assert result.payload["next_phase"] == "P22"
    
    # Check if monitor file was written coherently
    monitor_path = real_aiwg_setup / "reports" / "process_monitor_latest.json"
    assert monitor_path.exists()
    data = json.loads(monitor_path.read_text())
    assert data["current_phase"] == "P21"
    assert data["next_phase"] == "P22"

def test_dashboard_data_coherence(real_aiwg_setup):
    plane = CliControlPlane(aiwg_root=real_aiwg_setup)
    result = plane.run_command("dashboard-data")
    
    assert result.payload["current_phase"] == "P21"
    assert result.payload["next_phase"] == "P22"
    
    # Check HTML
    html_path = real_aiwg_setup / "reports" / "dashboard_l6_latest.html"
    assert html_path.exists()
    html = html_path.read_text()
    assert "P21" in html
    assert "P22" in html

def test_state_coherence_command(real_aiwg_setup):
    plane = CliControlPlane(aiwg_root=real_aiwg_setup)
    
    # Run status first to generate reports
    plane.run_command("status")
    plane.run_command("dashboard-data")
    
    # Now run coherence check
    result = plane.run_command("state-coherence")
    assert result.decision == "PASS"
    
    # Break coherence
    (real_aiwg_setup / "evolution" / "current_position.json").write_text(json.dumps({"current_phase": "P22"}))
    
    result = plane.run_command("state-coherence")
    assert result.decision == "FAIL"
