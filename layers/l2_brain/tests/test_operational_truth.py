import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import types
from pathlib import Path

from layers.l2_brain.governance.operational_truth import TruthCheck, TruthReport, TruthStatus
from layers.l2_brain.operational_truth_collectors import _dummied_check, _kuzu_check, collect_truth


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
    (repo / "layers/l2_brain/flat_brain").mkdir(parents=True)
    (repo / "layers/l1_nervous/tools_impl").mkdir(parents=True)
    (repo / ".aiwg/memory").mkdir(parents=True)
    (repo / "layers/l2_brain/flat_brain/model_router.py").write_text("class ModelRouter: pass\n")
    (repo / "layers/l2_brain/flat_brain/neuron_ledger.py").write_text("class NeuronLedger: pass\n")
    (repo / "layers/l2_brain/flat_brain/action_graph.py").write_text("class ActionGraph: pass\n")
    (repo / "layers/l2_brain/flat_brain/token_cost_ledger.py").write_text("class TokenCostLedger: pass\n")
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


def test_kuzu_probe_accepts_file_backed_database_when_kuzu_opens_it(tmp_path: Path, monkeypatch):
    memory = tmp_path / ".aiwg" / "memory"
    memory.mkdir(parents=True)
    (memory / "loci.db").write_bytes(b"kuzu")

    fake_kuzu = types.SimpleNamespace(
        Database=lambda path: {"path": path},
        Connection=lambda db: {"db": db},
    )
    monkeypatch.setitem(sys.modules, "kuzu", fake_kuzu)

    check = _kuzu_check(tmp_path, include_slow=True)

    assert check.status == TruthStatus.PASS


def test_dummied_probe_passes_when_control_socket_replies_pong(tmp_path: Path):
    import socket
    import threading

    socket_path = tmp_path / "dummied.sock"
    ready = threading.Event()

    def serve_once():
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(socket_path))
        server.listen(1)
        ready.set()
        conn, _ = server.accept()
        with conn:
            conn.recv(4096)
            conn.sendall(b'{"status":"ok","message":"PONG"}\n')
        server.close()

    thread = threading.Thread(target=serve_once, daemon=True)
    thread.start()
    assert ready.wait(timeout=1)

    check = _dummied_check(tmp_path, socket_path=socket_path)

    assert check.status == TruthStatus.PASS
    assert "control ping ok" in check.evidence[0]


def test_dummie_truth_cli_json_smoke():
    import sys
    out = subprocess.check_output(
        [sys.executable, "scripts/dummie_truth.py", "--json"],
        text=True,
    )
    payload = json.loads(out)

    assert "summary" in payload
    assert "checks" in payload
    assert payload["repo_root"]
