# Spec Reference: 192_embedding_mesh_foundation
import json
import pytest
from pathlib import Path
from layers.l2_brain.structural_hardening.matrix import StructuralTriageMatrix
from layers.l2_brain.structural_hardening.reporter import StructuralHardeningReporter
from layers.l2_brain.structural_hardening.cli import main


@pytest.fixture
def repo_env(tmp_path):
    repo_root = tmp_path
    
    # Create required reports structure
    reports_dir = repo_root / ".aiwg" / "reports"
    reports_dir.mkdir(parents=True)
    
    # Create fake semantic repo index
    index_data = {
        "generated_at": "2026-05-18T19:56:56Z",
        "files": [
            {"path": "layers/l2_brain/model_router.py", "classification": "UNKNOWN"},
            {"path": "layers/l2_brain/__init__.py", "classification": "UNKNOWN"},
            {"path": "pyproject.toml", "classification": "CONFIG"},
            {"path": "doc/specs/101_model_router.md", "classification": "SPEC"}
        ]
    }
    (reports_dir / "semantic_repo_index_latest.json").write_text(json.dumps(index_data))
    
    # Create directories physically
    (repo_root / "layers" / "l2_brain").mkdir(parents=True, exist_ok=True)
    (repo_root / "layers" / "l2_brain" / "model_router.py").touch()
    (repo_root / "layers" / "l2_brain" / "__init__.py").touch()
    (repo_root / "pyproject.toml").touch()
    
    (repo_root / "doc" / "specs").mkdir(parents=True, exist_ok=True)
    (repo_root / "doc" / "specs" / "101_model_router.md").write_text("spec_id: 101\nlayers/l2_brain/model_router.py")
    
    return repo_root


def test_triage_matrix_analysis(repo_env):
    matrix = StructuralTriageMatrix(str(repo_env))
    report = matrix.analyze()
    
    assert report.files_analyzed == 4
    # model_router has a spec, so it is ACTIVE_RUNTIME
    # __init__.py is active packaging glue, so ACTIVE_RUNTIME (with LOW risk)
    # pyproject.toml is CONFIG
    # 101_model_router.md is ACTIVE_SPEC
    # All are connected, no shadow candidates, so repo health status PASS
    assert report.repo_health_status == "PASS"
    assert report.summary_counts["ACTIVE_RUNTIME"] == 2
    assert report.summary_counts["CONFIG"] == 1
    assert report.summary_counts["ACTIVE_SPEC"] == 1


def test_triage_matrix_shadow_fails_health(repo_env):
    # Add a shadow candidate: a runtime file with no tests or specs
    (repo_env / "layers" / "l2_brain" / "orphan_runtime.py").touch()
    
    # Re-write the semantic repo index to include it
    reports_dir = repo_env / ".aiwg" / "reports"
    index_data = {
        "generated_at": "2026-05-18T19:56:56Z",
        "files": [
            {"path": "layers/l2_brain/model_router.py", "classification": "UNKNOWN"},
            {"path": "layers/l2_brain/__init__.py", "classification": "UNKNOWN"},
            {"path": "layers/l2_brain/orphan_runtime.py", "classification": "UNKNOWN"},
            {"path": "pyproject.toml", "classification": "CONFIG"},
            {"path": "doc/specs/101_model_router.md", "classification": "SPEC"}
        ]
    }
    (reports_dir / "semantic_repo_index_latest.json").write_text(json.dumps(index_data))
    
    matrix = StructuralTriageMatrix(str(repo_env))
    report = matrix.analyze()
    
    assert report.summary_counts["SHADOW_CANDIDATE"] == 1
    assert report.repo_health_status == "FAIL"


def test_reporter_writes_physical_files(repo_env):
    matrix = StructuralTriageMatrix(str(repo_env))
    report = matrix.analyze()
    
    reporter = StructuralHardeningReporter(str(repo_env))
    written = reporter.write_reports(report)
    
    assert Path(written["triage_json"]).exists()
    assert Path(written["triage_md"]).exists()
    assert Path(written["actions_json"]).exists()
    assert Path(written["actions_md"]).exists()
    
    # Check contents of md
    md_content = Path(written["triage_md"]).read_text()
    assert "pack_status: triage_completed" in md_content
    assert "repo_health_status: PASS" in md_content
    assert "ACTIVE_RUNTIME: 2" in md_content


def test_cli_execution(repo_env):
    exit_code = main(["--repo-root", str(repo_env), "--write-reports"])
    assert exit_code == 0
    
    reports_dir = repo_env / ".aiwg" / "reports"
    assert (reports_dir / "structural_hardening_triage_latest.json").exists()
    assert (reports_dir / "structural_hardening_triage_latest.md").exists()
