import hashlib
import json
from pathlib import Path

import pytest

from layers.l2_brain.context_package import ContextPackageBuilder


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _make_aiwg(tmp_path: Path, note_path: str = ".aiwg/notes/folders/f1/notes.md") -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P10"}})
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P9", "next_required_phase": "P10"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P10", "name": "FreshnessLedger + StaleMemoryDetector"})
    _write_json(aiwg / "reports" / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 10, "complete_triplets": 9}})

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
                    "linked_specs": ["doc/specs/112_folder_notes_noteplans.md"],
                    "linked_tests": ["layers/l2_brain/tests/test_context_package.py"],
                    "truth_rank": 40,
                    "token_role": "summary_only",
                    "risks": [],
                }
            ]
        },
    )
    return aiwg


def test_context_package_builder_creates_required_items(tmp_path: Path):
    aiwg = _make_aiwg(tmp_path)
    builder = ContextPackageBuilder(aiwg_root=aiwg)

    package, receipt = builder.build_context_package(mission_id="m1", phase="P10", budget_limit=1200, write_outputs=True)

    refs = {item.ref for item in package.items}
    assert "state:current_position" in refs
    assert "state:next_phase_seed" in refs
    assert "wm:project_world_model" in refs
    assert "coverage:spec_coverage_matrix" in refs

    assert receipt.kept_refs
    assert receipt.package_id == package.package_id

    assert (aiwg / "reports" / "context_package_latest.json").exists()
    assert (aiwg / "reports" / "context_receipt_latest.json").exists()


def test_context_package_builder_rejects_secret_like_evidence_refs(tmp_path: Path):
    aiwg = _make_aiwg(tmp_path, note_path=".env=SECRET_VALUE")
    builder = ContextPackageBuilder(aiwg_root=aiwg)

    with pytest.raises(ValueError):
        builder.build_context_package(mission_id="m1", phase="P10", write_outputs=False)


def test_context_package_json_roundtrip(tmp_path: Path):
    aiwg = _make_aiwg(tmp_path)
    builder = ContextPackageBuilder(aiwg_root=aiwg)
    package, receipt = builder.build_context_package(mission_id="m1", phase="P10", write_outputs=False)

    package_data = json.loads(json.dumps(package.to_dict()))
    receipt_data = json.loads(json.dumps(receipt.to_dict()))

    assert package_data["package_id"]
    assert receipt_data["receipt_id"]
