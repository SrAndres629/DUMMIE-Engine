import json
import importlib.util
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "watch_repo_events.py"


def run_watcher(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def load_watcher_module():
    spec = importlib.util.spec_from_file_location("watch_repo_events", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_help_has_no_side_effects(tmp_path):
    result = run_watcher("--help", cwd=tmp_path)

    assert result.returncode == 0
    assert "--root" in result.stdout
    assert not (tmp_path / ".aiwg").exists()


def test_once_dry_run_reports_events_without_writing(tmp_path):
    (tmp_path / "layers" / "l1_nervous").mkdir(parents=True)
    (tmp_path / "layers" / "l1_nervous" / "file.py").write_text("print('x')\n")

    result = run_watcher("--root", str(tmp_path), "--once", "--dry-run")

    assert result.returncode == 0
    assert "dry_run=True" in result.stdout
    assert "FILE_ADDED=1" in result.stdout
    assert not (tmp_path / ".aiwg").exists()


def test_once_writes_snapshot_and_events(tmp_path):
    tracked = tmp_path / "layers" / "l2_brain_local" / "file.py"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("old\n")

    result = run_watcher("--root", str(tmp_path), "--once")

    assert result.returncode == 0
    snapshot_path = tmp_path / ".aiwg" / "index" / "file_snapshot.json"
    events_path = tmp_path / ".aiwg" / "events" / "file_events.jsonl"
    assert snapshot_path.exists()
    assert events_path.exists()

    event = json.loads(events_path.read_text().splitlines()[0])
    assert event["event_type"] == "FILE_ADDED"
    assert event["path"] == "layers/l2_brain_local/file.py"
    assert event["old_sha256"] is None
    assert event["new_sha256"]
    assert event["layer"] == "l2_brain_local"
    assert event["six_d_context"]["authority_a"] == "WATCHER"
    assert event["six_d_context"]["intent_i"] == "OBSERVATION"
    assert event["six_d_context"]["lamport_t"] == 1
    assert {"locus_x", "locus_y", "locus_z"} <= set(event["six_d_context"])


def test_scan_ignores_dynamic_aiwg_and_outputs(tmp_path):
    watcher = load_watcher_module()
    (tmp_path / ".aiwg" / "workspaces" / "run").mkdir(parents=True)
    (tmp_path / ".aiwg" / "workspaces" / "run" / "ignored.txt").write_text("ignored\n")
    (tmp_path / ".aiwg" / "index").mkdir(parents=True)
    snapshot_path = tmp_path / ".aiwg" / "index" / "file_snapshot.json"
    events_path = tmp_path / ".aiwg" / "events" / "file_events.jsonl"
    snapshot_path.write_text("{}\n")

    snapshot = watcher.scan(tmp_path.resolve(), {snapshot_path.resolve(), events_path.resolve()})

    assert ".aiwg/index/file_snapshot.json" not in snapshot
    assert ".aiwg/workspaces/run/ignored.txt" not in snapshot
