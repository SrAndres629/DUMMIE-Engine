import json
import subprocess
from pathlib import Path

from operational_truth import TruthCheck, TruthReport, TruthStatus
from operational_truth_collectors import collect_truth


def test_truth_report_counts_statuses():
    report = TruthReport(
        repo_root="/repo",
        checks=[
            TruthCheck("l1.gateway.import", "L1", TruthStatus.PASS, ["import ok"]),
            TruthCheck("l3.budget", "L3", TruthStatus.DEGRADED, ["stub auditor"]),
            TruthCheck("l0.daemon", "L0", TruthStatus.BLOCKED, ["not running"]),
        ],
    )

    assert report.summary() == {
        "PASS": 1,
        "DEGRADED": 1,
        "BLOCKED": 1,
        "UNKNOWN": 0,
    }


def test_truth_report_serializes_status_values():
    report = TruthReport(
        repo_root="/repo",
        checks=[TruthCheck("l2.router", "L2", TruthStatus.PASS, ["ok"])],
    )

    payload = report.to_dict()

    assert payload["summary"]["PASS"] == 1
    assert payload["checks"][0]["status"] == "PASS"


def test_collect_truth_reports_existing_router_swarm_and_reward_assets(tmp_path: Path):
    repo = tmp_path
    (repo / "layers/l2_brain").mkdir(parents=True)
    (repo / "layers/l1_nervous/tools_impl").mkdir(parents=True)
    (repo / ".aiwg/memory").mkdir(parents=True)
    (repo / "layers/l2_brain/model_router.py").write_text("class ModelRouter: pass\n")
    (repo / "layers/l2_brain/neuron_ledger.py").write_text("class NeuronLedger: pass\n")
    (repo / "layers/l2_brain/action_graph.py").write_text("class ActionGraph: pass\n")
    (repo / "layers/l1_nervous/tools_impl/swarm.py").write_text("def register_swarm_tools(): pass\n")

    report = collect_truth(str(repo), include_slow=False)
    by_name = {check.name: check for check in report.checks}

    assert by_name["l2.model_router.file"].status == TruthStatus.PASS
    assert by_name["l2.neuron_ledger.file"].status == TruthStatus.PASS
    assert by_name["l2.action_graph.file"].status == TruthStatus.PASS
    assert by_name["l1.swarm_tools.file"].status == TruthStatus.PASS


def test_collect_truth_never_crashes_when_runtime_is_absent(tmp_path: Path):
    report = collect_truth(str(tmp_path), include_slow=True)

    assert report.repo_root == str(tmp_path)
    assert all(check.name for check in report.checks)
    assert set(report.summary()) == {"PASS", "DEGRADED", "BLOCKED", "UNKNOWN"}


def test_dummie_truth_cli_json_smoke():
    out = subprocess.check_output(
        ["python3", "scripts/dummie_truth.py", "--json"],
        text=True,
    )
    payload = json.loads(out)

    assert "summary" in payload
    assert "checks" in payload
    assert payload["repo_root"]
