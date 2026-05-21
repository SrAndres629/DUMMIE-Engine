import hashlib
import json
from pathlib import Path

from layers.l2_brain.context.context_quant_runtime import ContextQuantRuntime


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _make_aiwg(tmp_path: Path, stale_optional: bool = True) -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P10"}})
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P9", "next_required_phase": "P10"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P10", "name": "FreshnessLedger + StaleMemoryDetector"})
    _write_json(aiwg / "reports" / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 12, "complete_triplets": 11}})

    folder = root / "notes_src"
    folder.mkdir(parents=True, exist_ok=True)

    note = root / ".aiwg/notes/folders/f1/notes.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("note", encoding="utf-8")

    noteplan = root / ".aiwg/notes/folders/f1/noteplan.md"
    noteplan.parent.mkdir(parents=True, exist_ok=True)
    noteplan.write_text("plan", encoding="utf-8")

    expected_hash = hashlib.sha256("\ncount:0\npath:notes_src".encode("utf-8")).hexdigest()
    source_hash = "bad_hash" if stale_optional else expected_hash

    _write_json(
        aiwg / "notes" / "folder_notes_manifest.json",
        {
            "folders": [
                {
                    "folder_id": "f1",
                    "folder_path": "notes_src",
                    "note_path": ".aiwg/notes/folders/f1/notes.md",
                    "noteplan_path": ".aiwg/notes/folders/f1/noteplan.md",
                    "source_hash": source_hash,
                    "hash_method": "sha256(sorted_git_ls_files_plus_counts)",
                    "tracked_file_count": 0,
                    "freshness": {
                        "status": "fresh",
                        "invalidation_triggers": ["source_file_changed"],
                    },
                    "linked_specs": ["doc/specs/112_folder_notes_noteplans.md"],
                    "linked_tests": ["layers/l2_brain/tests/test_context_quant_runtime.py"],
                    "truth_rank": 40,
                    "token_role": "summary_only",
                    "risks": [],
                }
            ]
        },
    )
    return aiwg


def test_context_quant_runtime_preserves_required_under_low_budget(tmp_path: Path):
    aiwg = _make_aiwg(tmp_path, stale_optional=True)
    runtime = ContextQuantRuntime(aiwg_root=aiwg)

    result = runtime.build_context_for_phase(mission_id="m1", phase="P10", budget_limit=50, write_outputs=True)

    kept = set(result.kept_refs)
    assert "state:current_position" in kept
    assert "wm:project_world_model" in kept


def test_context_quant_runtime_drops_or_compresses_stale_optional_items(tmp_path: Path):
    aiwg = _make_aiwg(tmp_path, stale_optional=True)
    runtime = ContextQuantRuntime(aiwg_root=aiwg)

    result = runtime.build_context_for_phase(mission_id="m1", phase="P10", budget_limit=600, write_outputs=True)

    stale_ref = "note:f1"
    assert stale_ref in set(result.compressed_refs) | set(result.dropped_refs)

    assert (aiwg / "reports" / "context_quant_result_latest.json").exists()
    assert (aiwg / "reports" / "context_receipt_latest.json").exists()
