import json
import pytest
from pathlib import Path
from layers.l2_brain.governance.state_coherence_guard import StateCoherenceGuard, run_state_coherence_guard

@pytest.fixture
def temp_aiwg(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    current = {"current_phase": "P21"}
    seed = {"next_phase": "P22"}
    
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    return aiwg

def test_guard_pass_when_coherent(temp_aiwg):
    repo = temp_aiwg / "reports"
    payload = {"current_phase": "P21", "next_phase": "P22"}
    
    (repo / "process_monitor_latest.json").write_text(json.dumps(payload))
    (repo / "dashboard_l6_latest.json").write_text(json.dumps(payload))
    
    # Mock CLI status
    cli_payload = {
        "command": "status",
        "payload": payload
    }
    (repo / "cli_control_plane_latest.json").write_text(json.dumps(cli_payload))
    
    # Create HTML
    html = f"<div class=\"v\">P21</div><div class=\"v\">P22</div>"
    (repo / "dashboard_l6_latest.html").write_text(html)
    
    guard = StateCoherenceGuard(aiwg_root=temp_aiwg)
    report = guard.check_state_coherence()
    
    assert report.decision == "PASS"
    assert len([f for f in report.findings if f.severity == "ERROR"]) == 0

def test_guard_fail_when_stale(temp_aiwg):
    repo = temp_aiwg / "reports"
    stale = {"current_phase": "P17", "next_phase": "P18"}
    
    (repo / "process_monitor_latest.json").write_text(json.dumps(stale))
    
    guard = StateCoherenceGuard(aiwg_root=temp_aiwg)
    report = guard.check_state_coherence()
    
    assert report.decision == "FAIL"
    findings = [f for f in report.findings if f.artifact == "process_monitor_latest.json" and f.severity == "ERROR"]
    assert len(findings) > 0

def test_guard_fail_when_html_stale(temp_aiwg):
    repo = temp_aiwg / "reports"
    payload = {"current_phase": "P21", "next_phase": "P22"}
    (repo / "process_monitor_latest.json").write_text(json.dumps(payload))
    (repo / "dashboard_l6_latest.json").write_text(json.dumps(payload))
    
    html = "<div>Current Phase</div><div class=\"v\">P17</div>"
    (repo / "dashboard_l6_latest.html").write_text(html)
    
    guard = StateCoherenceGuard(aiwg_root=temp_aiwg)
    report = guard.check_state_coherence()
    
    assert report.decision == "FAIL"
    assert any("HTML" in f.message for f in report.findings)
