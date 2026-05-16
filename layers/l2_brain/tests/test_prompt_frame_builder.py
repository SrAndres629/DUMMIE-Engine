import hashlib
import json
from pathlib import Path

import pytest

from layers.l2_brain.prompt_frame_builder import PromptFrameBuilder


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_aiwg(tmp_path: Path, note_path: str = ".aiwg/notes/folders/f1/notes.md") -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P14"}})
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P13", "next_required_phase": "P14"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P14", "name": "PromptFrameBuilder + PromptCacheLedger"})
    _write_json(aiwg / "reports" / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 100, "complete_triplets": 97}})

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
                    "linked_tests": ["layers/l2_brain/tests/test_prompt_frame_builder.py"],
                    "truth_rank": 40,
                    "token_role": "summary_only",
                    "risks": [],
                }
            ]
        },
    )
    return aiwg


def test_prompt_frame_builder_builds_from_quantized_context(tmp_path: Path):
    aiwg = _prepare_aiwg(tmp_path)
    builder = PromptFrameBuilder(aiwg_root=aiwg)

    frame = builder.build_prompt_frame_for_phase(
        mission_id="m1",
        phase_id="P14",
        budget_limit=300,
        write_output=True,
    )

    assert frame.context_refs
    assert "state:current_position" in frame.context_refs
    assert frame.receipt_ref == ".aiwg/reports/context_receipt_latest.json"
    assert frame.source_hash

    for ref in frame.context_refs:
        assert ref not in {".", "layers", "doc", ".aiwg"}

    latest = aiwg / "reports" / "prompt_frame_latest.json"
    assert latest.exists()


def test_prompt_frame_builder_rejects_secret_or_private_refs(tmp_path: Path):
    aiwg = _prepare_aiwg(tmp_path, note_path=".env=SECRET")
    builder = PromptFrameBuilder(aiwg_root=aiwg)

    with pytest.raises(ValueError):
        builder.build_prompt_frame_for_phase(mission_id="m1", phase_id="P14", write_output=False)


def test_prompt_frame_builder_source_hash_stable(tmp_path: Path):
    aiwg = _prepare_aiwg(tmp_path)
    builder = PromptFrameBuilder(aiwg_root=aiwg)

    frame1 = builder.build_prompt_frame_for_phase(mission_id="m1", phase_id="P14", budget_limit=300, write_output=False)
    frame2 = builder.build_prompt_frame_for_phase(mission_id="m1", phase_id="P14", budget_limit=300, write_output=False)

    assert frame1.source_hash == frame2.source_hash
