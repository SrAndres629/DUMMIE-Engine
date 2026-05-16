import json
import pytest
from pathlib import Path
from layers.l2_brain.chaos_regression_testing import ChaosRegressionTester

@pytest.fixture
def chaos_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    return aiwg

def test_chaos_runs_all_scenarios(chaos_env):
    tester = ChaosRegressionTester(aiwg_root=chaos_env)
    report = tester.run_tests()
    assert report.scenarios_total == 4
    assert report.decision == "PASS"
    assert len(report.findings) == 4

def test_chaos_detects_unsafe_allowance(chaos_env):
    tester = ChaosRegressionTester(aiwg_root=chaos_env)
    # Monkeypatch to simulate a failure in detection
    tester._simulate_scenario = lambda s: "ALLOW" 
    report = tester.run_tests()
    assert report.decision == "FAIL"
    assert report.scenarios_failed > 0
