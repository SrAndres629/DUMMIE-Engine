import json
from pathlib import Path

from layers.l2_brain.structural_hardening.cli import build_structural_hardening_triage


def test_triage_cli_generates_reports_without_internet(tmp_path):
    repo = tmp_path / "repo"
    reports = repo / ".aiwg" / "reports"
    reports.mkdir(parents=True)
    (repo / "layers" / "l2_brain" / "tests").mkdir(parents=True)
    (repo / "doc" / "specs").mkdir(parents=True)

    semantic_index = {
        "files": [
            {"path": "layers/l2_brain/__init__.py", "classification": "UNKNOWN", "content_type": "CODE"},
            {"path": "layers/l2_brain/model_router.py", "classification": "ACTIVE_RUNTIME", "content_type": "CODE"},
            {"path": "layers/l2_brain/tests/test_model_router.py", "classification": "TEST", "content_type": "TEST"},
            {"path": "doc/specs/190_model_router.md", "classification": "SPEC", "content_type": "SPEC"},
            {"path": "layers/l2_brain/proto/memory_pb2.py", "classification": "GENERATED", "content_type": "CODE"},
            {"path": "doc/.deprecated/old_note.md", "classification": "LEGACY", "content_type": "TEXT"},
            {"path": "pyproject.toml", "classification": "CONFIG", "content_type": "CONFIG"},
            {"path": ".aiwg/reports/semantic_repo_index_latest.json", "classification": "REPORT", "content_type": "REPORT"},
        ]
    }
    semantic_matrix = {
        "records": [
            {
                "module": "layers/l2_brain/model_router.py",
                "likely_specs": ["doc/specs/190_model_router.md"],
                "likely_tests": ["layers/l2_brain/tests/test_model_router.py"],
            }
        ]
    }

    (reports / "semantic_repo_index_latest.json").write_text(json.dumps(semantic_index), encoding="utf-8")
    (reports / "semantic_hardening_matrix_latest.json").write_text(json.dumps(semantic_matrix), encoding="utf-8")

    # physical files for evidence checks
    (repo / "layers" / "l2_brain" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "layers" / "l2_brain" / "model_router.py").write_text("def route():\n    return 1\n", encoding="utf-8")
    (repo / "layers" / "l2_brain" / "tests" / "test_model_router.py").write_text("def test_route():\n    assert True\n", encoding="utf-8")
    (repo / "doc" / "specs" / "190_model_router.md").write_text("spec_id: 190\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    payload, exit_code = build_structural_hardening_triage(
        repo_root=str(repo),
        write_reports_flag=True,
        max_actions=50,
        include_low_risk=False,
        fail_on_critical=False,
    )

    assert exit_code == 0
    assert payload["pack_status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert payload["repo_health_status"] in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}

    triage_json = reports / "structural_hardening_triage_latest.json"
    triage_md = reports / "structural_hardening_triage_latest.md"
    actions_json = reports / "structural_hardening_actions_latest.json"
    actions_md = reports / "structural_hardening_actions_latest.md"

    assert triage_json.exists()
    assert triage_md.exists()
    assert actions_json.exists()
    assert actions_md.exists()

    report = json.loads(triage_json.read_text(encoding="utf-8"))
    assert "pack_status" in report
    assert "repo_health_status" in report
    assert report["pack_name"].startswith("Structural Hardening Pack 2")

    findings = {f["path"]: f for f in report["findings"]}
    assert findings["layers/l2_brain/__init__.py"]["proposed_class"] == "ACTIVE_RUNTIME"
