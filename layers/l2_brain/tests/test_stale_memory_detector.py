import json
from pathlib import Path

from layers.l2_brain.freshness_ledger import build_freshness_ledger
from layers.l2_brain.stale_memory_detector import detect_stale_memory


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _build_aiwg_with_stale(tmp_path: Path) -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0"})
    _write_json(
        aiwg / "reports" / "spec_coverage_matrix.json",
        {"coverage_summary": {"spec_families_total": 2, "complete_triplets": 1}},
    )

    folder = root / "notes_src"
    folder.mkdir(parents=True, exist_ok=True)
    note = root / ".aiwg/notes/folders/f1/notes.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("note", encoding="utf-8")
    # missing noteplan on purpose and wrong source hash to force stale

    _write_json(
        aiwg / "notes" / "folder_notes_manifest.json",
        {
            "folders": [
                {
                    "folder_id": "f1",
                    "folder_path": "notes_src",
                    "note_path": ".aiwg/notes/folders/f1/notes.md",
                    "noteplan_path": ".aiwg/notes/folders/f1/noteplan.md",
                    "source_hash": "definitely_wrong_hash",
                    "hash_method": "sha256(sorted_git_ls_files_plus_counts)",
                    "tracked_file_count": 0,
                    "freshness": {
                        "status": "fresh",
                        "invalidation_triggers": ["source_file_changed"],
                    },
                    "risks": [],
                }
            ]
        },
    )
    return aiwg


def test_stale_memory_detector_detects_stale_and_missing(tmp_path: Path):
    aiwg = _build_aiwg_with_stale(tmp_path)
    ledger = build_freshness_ledger(aiwg_root=aiwg, write_report=True)
    report = detect_stale_memory(aiwg_root=aiwg, ledger=ledger, write_report=True)

    finding_types = {f.finding_type for f in report.findings}
    assert "stale_freshness" in finding_types
    assert "folder_note_hash_mismatch" in finding_types
    assert "missing_noteplan_path" in finding_types

    output = aiwg / "reports" / "stale_memory_report.json"
    assert output.exists()


def test_stale_memory_detector_reports_missing_world_model(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _write_json(aiwg / "reports" / "spec_coverage_matrix.json", {"coverage_summary": {}})
    _write_json(aiwg / "notes" / "folder_notes_manifest.json", {"folders": []})

    report = detect_stale_memory(aiwg_root=aiwg, write_report=False)
    finding_types = {f.finding_type for f in report.findings}
    assert "missing_world_model" in finding_types
