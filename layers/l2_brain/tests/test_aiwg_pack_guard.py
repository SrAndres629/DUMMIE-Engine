import os
import json
import pytest
import subprocess
from datetime import datetime

# Path constants matching scripts/aiwg_pack_guard.py
AIWG_DIR = ".aiwg"
STATE_TRUTH = os.path.join(AIWG_DIR, "state", "current_truth.json")
ROADMAP_JSON = os.path.join(AIWG_DIR, "roadmap", "pack_roadmap_to_6_1.json")
ACTIVE_PACK = os.path.join(AIWG_DIR, "packs", "active_pack.json")
HISTORY_JSONL = os.path.join(AIWG_DIR, "packs", "pack_execution_history.jsonl")
DISTANCE_JSON = os.path.join(AIWG_DIR, "metrics", "project_distance_to_6_1.json")
CRITIQUE_JSON = os.path.join(AIWG_DIR, "reports", "pack_self_critique_latest.json")
DECISION_LOG = os.path.join(AIWG_DIR, "decisions", "decision_log.jsonl")
EVIDENCE_JSON = os.path.join(AIWG_DIR, "reports", "pack_validation_evidence_latest.json")

def test_current_truth_mandatory_fields():
    """Assert current_truth.json contains all mandatory metadata fields required by governance."""
    assert os.path.exists(STATE_TRUTH), "current_truth.json must exist in .aiwg/state/"
    
    with open(STATE_TRUTH, "r", encoding="utf-8") as f:
        truth = json.load(f)
        
    mandatory_keys = [
        "generated_at", "head_commit", "branch", "origin_synced",
        "repo_health_status", "semantic_mode", "index_mode",
        "current_pack", "last_completed_pack", "next_pack",
        "critical_count", "high_count", "shadow_candidate_count",
        "unknown_count", "orphan_test_candidate_count",
        "degraded_embeddings", "real_text_fast_embeddings",
        "vector_spaces_used", "active_capabilities", "degraded_capabilities",
        "blocked_capabilities", "latest_reports", "source_of_truth_files"
    ]
    
    for key in mandatory_keys:
        assert key in truth, f"Missing mandatory field '{key}' in current_truth.json"

def test_active_pack_rollback_and_tests():
    """Assert active_pack.json possesses a valid rollback plan, tests required, and stop conditions."""
    assert os.path.exists(ACTIVE_PACK), "active_pack.json must exist in .aiwg/packs/"
    
    with open(ACTIVE_PACK, "r", encoding="utf-8") as f:
        active = json.load(f)
        
    assert "pack_id" in active, "active_pack.json missing pack_id"
    assert "rollback_plan" in active or "rollback" in active, "active_pack.json missing rollback plan"
    assert "tests_required" in active or "tests" in active, "active_pack.json missing tests_required"
    assert "stop_conditions" in active, "active_pack.json missing stop_conditions"
    
    rollback = active.get("rollback_plan") or active.get("rollback")
    tests = active.get("tests_required") or active.get("tests")
    stops = active.get("stop_conditions")
    
    assert isinstance(rollback, str) and len(rollback.strip()) > 0, "Rollback plan must be a non-empty string"
    assert isinstance(tests, list) and len(tests) > 0, "tests_required must be a non-empty list"
    assert isinstance(stops, list) and len(stops) > 0, "stop_conditions must be a non-empty list"

def test_self_critique_fails_if_unverified(tmp_path, monkeypatch):
    """Assert that self-critique command fails if mandatory arguments are missing/UNVERIFIED."""
    import scripts.aiwg_pack_guard as guard
    
    class DummyArgs:
        what = None  # Missing
        broken = "Ninguno"  # Optimistic pattern (rejected)
        metrics = "Metrics updated"
        shallow = "Shallow tests identified"
        stale = "Stale reports identified"
        assumptions = "Some assumptions"
        repairs = "Repairs identified"
        degraded = "Advances degraded details"
        goal = "Moves towards Pack 6.1"
        
    temp_active = os.path.join(tmp_path, "active_pack.json")
    with open(temp_active, "w", encoding="utf-8") as f:
        json.dump({"pack_id": "TEST_PACK"}, f)
        
    monkeypatch.setattr(guard, "ACTIVE_PACK", temp_active)
    monkeypatch.setattr(guard, "CRITIQUE_JSON", os.path.join(tmp_path, "critique.json"))
    monkeypatch.setattr(guard, "CRITIQUE_MD", os.path.join(tmp_path, "critique.md"))
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_self_critique(DummyArgs())
    assert excinfo.value.code != 0, "self-critique must exit with non-zero code if any field is UNVERIFIED"

def test_closeout_fails_if_missing_self_critique(tmp_path, monkeypatch):
    """Assert that closeout subcommand fails if self-critique JSON file is missing."""
    import scripts.aiwg_pack_guard as guard
    
    non_existent = os.path.join(tmp_path, "missing_critique.json")
    monkeypatch.setattr(guard, "CRITIQUE_JSON", non_existent)
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0, "closeout should fail when self-critique is missing"

def test_closeout_fails_if_missing_evidence(tmp_path, monkeypatch):
    """Assert that closeout fails if validation evidence is missing."""
    import scripts.aiwg_pack_guard as guard
    
    temp_critique = os.path.join(tmp_path, "critique.json")
    with open(temp_critique, "w", encoding="utf-8") as f:
        json.dump({
            "answers": {
                "what_implemented": "Implemented tests",
                "what_broken": "None verified",
                "metrics_changed": "None",
                "tests_shallow": "None",
                "reports_stale": "None",
                "assumptions": "None",
                "repairs_needed": "None",
                "advances_degraded": "None",
                "advances_goal_6_1": "Yes"
            }
        }, f)
        
    monkeypatch.setattr(guard, "CRITIQUE_JSON", temp_critique)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", os.path.join(tmp_path, "missing_evidence.json"))
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0, "closeout should fail when validation evidence is missing"

def test_closeout_fails_if_stale_evidence_commit(tmp_path, monkeypatch):
    """Assert that closeout fails if validation evidence commit hash is stale."""
    import scripts.aiwg_pack_guard as guard
    
    temp_critique = os.path.join(tmp_path, "critique.json")
    with open(temp_critique, "w", encoding="utf-8") as f:
        json.dump({
            "answers": {
                "what_implemented": "Implemented tests",
                "what_broken": "None verified",
                "metrics_changed": "None",
                "tests_shallow": "None",
                "reports_stale": "None",
                "assumptions": "None",
                "repairs_needed": "None",
                "advances_degraded": "None",
                "advances_goal_6_1": "Yes"
            }
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    with open(temp_evidence, "w", encoding="utf-8") as f:
        json.dump({
            "exit_code": 0,
            "commit": "stale_hash_value",
            "run_by_runner": True,
            "stdout_log_path": "manual",
            "duration_seconds": 0.0,
            "command": "pytest && validate_specs_docs"
        }, f)
        
    monkeypatch.setattr(guard, "CRITIQUE_JSON", temp_critique)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "get_git_head", lambda: "actual_git_head_hash")
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0, "closeout should fail when evidence commit is stale"

def test_closeout_fails_if_invalid_roadmap_sha(tmp_path, monkeypatch):
    """Assert that closeout fails if any source_of_truth_commit in roadmap is invalid."""
    import scripts.aiwg_pack_guard as guard
    
    temp_critique = os.path.join(tmp_path, "critique.json")
    with open(temp_critique, "w", encoding="utf-8") as f:
        json.dump({
            "answers": {
                "what_implemented": "Implemented tests",
                "what_broken": "None verified",
                "metrics_changed": "None",
                "tests_shallow": "None",
                "reports_stale": "None",
                "assumptions": "None",
                "repairs_needed": "None",
                "advances_degraded": "None",
                "advances_goal_6_1": "Yes"
            }
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    with open(temp_evidence, "w", encoding="utf-8") as f:
        json.dump({
            "exit_code": 0,
            "commit": "actual_hash",
            "run_by_runner": True,
            "stdout_log_path": "manual",
            "duration_seconds": 0.0,
            "command": "pytest && validate_specs_docs"
        }, f)
        
    temp_roadmap = os.path.join(tmp_path, "roadmap.json")
    with open(temp_roadmap, "w", encoding="utf-8") as f:
        json.dump({
            "packs": [
                {
                    "pack_id": "PACK_2.3",
                    "source_of_truth_commit": "invalid_commit_format(l2_brain)"  # Invalid!
                }
            ]
        }, f)
        
    temp_active = os.path.join(tmp_path, "active.json")
    with open(temp_active, "w", encoding="utf-8") as f:
        json.dump({
            "pack_id": "AIWG_KERNEL_0.1",
            "rollback_plan": "Revert change",
            "stop_conditions": ["Condition 1"],
            "tests_required": ["test_aiwg_pack_guard.py"]
        }, f)
        
    temp_truth = os.path.join(tmp_path, "truth.json")
    with open(temp_truth, "w", encoding="utf-8") as f:
        json.dump({
            "current_pack": "AIWG_KERNEL_0.1",
            "head_commit": "actual_hash"
        }, f)
        
    monkeypatch.setattr(guard, "CRITIQUE_JSON", temp_critique)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "ROADMAP_JSON", temp_roadmap)
    monkeypatch.setattr(guard, "ACTIVE_PACK", temp_active)
    monkeypatch.setattr(guard, "STATE_TRUTH", temp_truth)
    monkeypatch.setattr(guard, "DISTANCE_JSON", os.path.join(tmp_path, "distance.json"))
    monkeypatch.setattr(guard, "HISTORY_JSONL", os.path.join(tmp_path, "history.jsonl"))
    monkeypatch.setattr(guard, "DECISION_LOG", os.path.join(tmp_path, "decision_log.jsonl"))
    monkeypatch.setattr(guard, "get_git_head", lambda: "actual_hash")
    
    # Mock files exist
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0, "closeout should fail if roadmap contains invalid source of truth commit format"

def test_distance_report_contains_pack_6_1():
    """Assert that project_distance_to_6_1 JSON and MD files reference the long-term Pack 6.1 objective."""
    assert os.path.exists(DISTANCE_JSON), "project_distance_to_6_1.json must exist"
    
    with open(DISTANCE_JSON, "r", encoding="utf-8") as f:
        dist = json.load(f)
        
    assert "golden_path_remaining" in dist or "current_score" in dist, "Missing progress indicators"
    
    # Verify MD file mentions Pack 6.1
    md_path = DISTANCE_JSON.replace(".json", ".md")
    assert os.path.exists(md_path), "project_distance_to_6_1.md must exist"
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    assert "Pack 6.1" in md_content or "6.1" in md_content, "Distance markdown must reference target Pack 6.1"

def test_next_pack_skip_prevention(tmp_path, monkeypatch):
    """Assert that next-pack command refuses to proceed to Pack 3.2 if last completed is not Pack 3.1."""
    import scripts.aiwg_pack_guard as guard
    
    temp_truth = os.path.join(tmp_path, "truth.json")
    with open(temp_truth, "w", encoding="utf-8") as f:
        json.dump({
            "last_completed_pack": "PACK_3.0", # Violates PACK_3.1 requirement
            "next_pack": "PACK_3.2"
        }, f)
        
    monkeypatch.setattr(guard, "STATE_TRUTH", temp_truth)
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_next_pack(None)
    assert excinfo.value.code != 0, "next-pack should fail if we attempt to skip PACK_3.1"

def test_pack_history_valid_entries():
    """Assert that pack_execution_history.jsonl has valid structured JSON objects for each record."""
    assert os.path.exists(HISTORY_JSONL), "pack_execution_history.jsonl must exist"
    
    with open(HISTORY_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            assert "pack_id" in record
            assert "status" in record
            assert "commit" in record
            assert "branch" in record
            assert record["status"] in ["COMPLETED", "BLOCKED", "FAILED_NEEDS_REPAIR"]

def test_decision_log_valid_entries():
    """Assert that decision_log.jsonl contains correctly structured decision tracking rows."""
    assert os.path.exists(DECISION_LOG), "decision_log.jsonl must exist"
    
    with open(DECISION_LOG, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            assert "decision_id" in record
            assert "date" in record
            assert "decision" in record
            assert "context" in record
            assert "consequences" in record

def test_run_required_success(tmp_path, monkeypatch):
    """Assert run-required runs dummy echo command successfully, creating logs and evidence."""
    import scripts.aiwg_pack_guard as guard
    
    temp_active = os.path.join(tmp_path, "active_pack.json")
    with open(temp_active, "w", encoding="utf-8") as f:
        json.dump({
            "pack_id": "TEST_RUNNER_PACK",
            "commands_required": ["echo 'Successful Validation'"]
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    temp_evidence_md = os.path.join(tmp_path, "evidence.md")
    
    monkeypatch.setattr(guard, "ACTIVE_PACK", temp_active)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "EVIDENCE_MD", temp_evidence_md)
    monkeypatch.setattr(guard, "AIWG_DIR", str(tmp_path))
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_run_required(None)
    assert excinfo.value.code == 0
    
    log_dir = os.path.join(tmp_path, "reports", "validation_logs", "TEST_RUNNER_PACK")
    assert os.path.exists(log_dir)
    assert os.path.exists(os.path.join(log_dir, "stdout.log"))
    assert os.path.exists(os.path.join(log_dir, "stderr.log"))
    
    with open(temp_evidence, "r", encoding="utf-8") as f:
        ev = json.load(f)
    assert ev["exit_code"] == 0
    assert ev["run_by_runner"] is True
    assert "stdout.log" in ev["stdout_log_path"]
    assert ev["duration_seconds"] >= 0.0

def test_run_required_failure(tmp_path, monkeypatch):
    """Assert run-required records non-zero exit code if command fails."""
    import scripts.aiwg_pack_guard as guard
    
    temp_active = os.path.join(tmp_path, "active_pack.json")
    with open(temp_active, "w", encoding="utf-8") as f:
        json.dump({
            "pack_id": "TEST_RUNNER_PACK",
            "commands_required": ["false"]
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    temp_evidence_md = os.path.join(tmp_path, "evidence.md")
    
    monkeypatch.setattr(guard, "ACTIVE_PACK", temp_active)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "EVIDENCE_MD", temp_evidence_md)
    monkeypatch.setattr(guard, "AIWG_DIR", str(tmp_path))
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_run_required(None)
    assert excinfo.value.code != 0
    
    with open(temp_evidence, "r", encoding="utf-8") as f:
        ev = json.load(f)
    assert ev["exit_code"] != 0
    assert ev["result"] == "FAILED"

def test_run_required_protection(tmp_path, monkeypatch):
    """Assert run-required raises error/exit if python3 is used directly for semantic index scripts."""
    import scripts.aiwg_pack_guard as guard
    
    temp_active = os.path.join(tmp_path, "active_pack.json")
    with open(temp_active, "w", encoding="utf-8") as f:
        json.dump({
            "pack_id": "TEST_RUNNER_PACK",
            "commands_required": ["python3 scripts/semantic_index_updater.py"]
        }, f)
        
    monkeypatch.setattr(guard, "ACTIVE_PACK", temp_active)
    monkeypatch.setattr(guard, "AIWG_DIR", str(tmp_path))
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_run_required(None)
    assert excinfo.value.code != 0

def test_closeout_fails_if_non_runner_evidence(tmp_path, monkeypatch):
    """Assert that closeout fails if evidence ledger was manual or has invalid schema."""
    import scripts.aiwg_pack_guard as guard
    
    temp_critique = os.path.join(tmp_path, "critique.json")
    with open(temp_critique, "w", encoding="utf-8") as f:
        json.dump({
            "answers": {
                "what_implemented": "Implemented tests",
                "what_broken": "None verified",
                "metrics_changed": "None",
                "tests_shallow": "None",
                "reports_stale": "None",
                "assumptions": "None",
                "repairs_needed": "None",
                "advances_degraded": "None",
                "advances_goal_6_1": "Yes"
            }
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    with open(temp_evidence, "w", encoding="utf-8") as f:
        json.dump({
            "exit_code": 0,
            "commit": "actual_hash"
        }, f)
        
    monkeypatch.setattr(guard, "CRITIQUE_JSON", temp_critique)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "get_git_head", lambda: "actual_hash")
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0

def test_closeout_fails_if_missing_pytest_or_validate_specs_docs(tmp_path, monkeypatch):
    """Assert closeout fails if pytest or validate_specs_docs were not part of execution evidence."""
    import scripts.aiwg_pack_guard as guard
    
    temp_critique = os.path.join(tmp_path, "critique.json")
    with open(temp_critique, "w", encoding="utf-8") as f:
        json.dump({
            "answers": {
                "what_implemented": "Implemented tests",
                "what_broken": "None verified",
                "metrics_changed": "None",
                "tests_shallow": "None",
                "reports_stale": "None",
                "assumptions": "None",
                "repairs_needed": "None",
                "advances_degraded": "None",
                "advances_goal_6_1": "Yes"
            }
        }, f)
        
    temp_evidence = os.path.join(tmp_path, "evidence.json")
    with open(temp_evidence, "w", encoding="utf-8") as f:
        json.dump({
            "exit_code": 0,
            "commit": "actual_hash",
            "run_by_runner": True,
            "stdout_log_path": "manual",
            "duration_seconds": 0.0,
            "command": "echo hello"
        }, f)
        
    monkeypatch.setattr(guard, "CRITIQUE_JSON", temp_critique)
    monkeypatch.setattr(guard, "EVIDENCE_JSON", temp_evidence)
    monkeypatch.setattr(guard, "get_git_head", lambda: "actual_hash")
    
    with pytest.raises(SystemExit) as excinfo:
        guard.run_closeout(None)
    assert excinfo.value.code != 0
