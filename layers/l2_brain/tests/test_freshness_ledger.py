import hashlib
import json
from pathlib import Path

import pytest

from layers.l2_brain.freshness_ledger import (
    FreshnessEntry,
    build_freshness_ledger,
    load_freshness_ledger,
    _sanitize_evidence_refs,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _make_min_aiwg(tmp_path: Path, note_path: str = ".aiwg/notes/folders/f1/notes.md") -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0"})
    _write_json(
        aiwg / "reports" / "spec_coverage_matrix.json",
        {"coverage_summary": {"spec_families_total": 1, "complete_triplets": 1}},
    )

    folder = root / "notes_src"
    folder.mkdir(parents=True, exist_ok=True)

    (root / note_path).parent.mkdir(parents=True, exist_ok=True)
    (root / note_path).write_text("note", encoding="utf-8")
    noteplan_path = ".aiwg/notes/folders/f1/noteplan.md"
    (root / noteplan_path).parent.mkdir(parents=True, exist_ok=True)
    (root / noteplan_path).write_text("plan", encoding="utf-8")

    expected_hash = hashlib.sha256("\ncount:0\npath:notes_src".encode("utf-8")).hexdigest()

    _write_json(
        aiwg / "notes" / "folder_notes_manifest.json",
        {
            "folders": [
                {
                    "folder_id": "f1",
                    "folder_path": "notes_src",
                    "note_path": note_path,
                    "noteplan_path": noteplan_path,
                    "source_hash": expected_hash,
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


def test_freshness_ledger_builds_from_manifest(tmp_path: Path):
    aiwg = _make_min_aiwg(tmp_path)

    ledger = build_freshness_ledger(aiwg_root=aiwg, write_report=True)
    assert ledger.entries

    folder_entry = next(e for e in ledger.entries if e.artifact_id == "folder_note:f1")
    assert folder_entry.freshness_status == "fresh"
    assert folder_entry.hash_method == "sha256(sorted_git_ls_files_plus_counts)"

    output = aiwg / "reports" / "freshness_ledger.json"
    assert output.exists()

    loaded = load_freshness_ledger(output)
    assert any(e.artifact_id == "folder_note:f1" for e in loaded.entries)


def test_freshness_ledger_rejects_private_or_secret_evidence_refs():
    with pytest.raises(ValueError):
        _sanitize_evidence_refs(["chain_of_thought: hidden"])
    with pytest.raises(ValueError):
        _sanitize_evidence_refs([".env=SECRET_VALUE"])


def test_freshness_entry_json_roundtrip(tmp_path: Path):
    aiwg = _make_min_aiwg(tmp_path)
    ledger = build_freshness_ledger(aiwg_root=aiwg, write_report=False)

    payload = ledger.to_dict()
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert decoded["summary"]["total"] >= 1
    assert decoded["entries"][0]["artifact_id"]
