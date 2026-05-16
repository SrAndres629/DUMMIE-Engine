import hashlib
import json
from pathlib import Path

from layers.l2_brain.context_efficiency_benchmark import ContextEfficiencyBenchmark
from layers.l2_brain.evolution_flywheel_runtime import EvolutionFlywheelRuntime
from layers.l2_brain.prompt_cache_ledger import PromptCacheLedger
from layers.l2_brain.prompt_frame_builder import PromptFrameBuilder
from layers.l2_brain.restart_integration_gate import RestartIntegrationGate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_aiwg(tmp_path: Path) -> Path:
    root = tmp_path
    aiwg = root / ".aiwg"

    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P14"}})
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P13", "next_required_phase": "P14"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P14", "name": "PromptFrameBuilder + PromptCacheLedger"})
    (aiwg / "evolution" / "phases.yaml").parent.mkdir(parents=True, exist_ok=True)
    (aiwg / "evolution" / "phases.yaml").write_text("phases:\n  - id: P14\n  - id: P15\n  - id: P16\n  - id: P17\n  - id: P18\n", encoding="utf-8")
    _write_json(
        aiwg / "evolution" / "phase_dependencies.graph.json",
        {
            "edges": [
                {"from": "P14", "to": "P15"},
                {"from": "P15", "to": "P16"},
                {"from": "P16", "to": "P17"},
                {"from": "P17", "to": "P18"},
            ]
        },
    )
    _write_json(aiwg / "reports" / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 100, "complete_triplets": 97}})

    folder = root / "notes_src"
    folder.mkdir(parents=True, exist_ok=True)
    note = root / ".aiwg/notes/folders/f1/notes.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("note", encoding="utf-8")
    noteplan = root / ".aiwg/notes/folders/f1/noteplan.md"
    noteplan.parent.mkdir(parents=True, exist_ok=True)
    noteplan.write_text("plan", encoding="utf-8")

    expected_hash = hashlib.sha256("\ncount:0\npath:notes_src".encode("utf-8")).hexdigest()
    _write_json(
        aiwg / "notes" / "folder_notes_manifest.json",
        {
            "folders": [
                {
                    "folder_id": "f1",
                    "folder_path": "notes_src",
                    "note_path": ".aiwg/notes/folders/f1/notes.md",
                    "noteplan_path": ".aiwg/notes/folders/f1/noteplan.md",
                    "source_hash": expected_hash,
                    "hash_method": "sha256(sorted_git_ls_files_plus_counts)",
                    "tracked_file_count": 0,
                    "freshness": {
                        "status": "fresh",
                        "invalidation_triggers": ["source_file_changed"],
                    },
                    "linked_specs": ["doc/specs/112_folder_notes_noteplans.md"],
                    "linked_tests": ["layers/l2_brain/tests/test_prompt_runtime_integration.py"],
                    "truth_rank": 40,
                    "token_role": "summary_only",
                    "risks": [],
                }
            ]
        },
    )
    return aiwg


def test_prompt_runtime_integration_pipeline(tmp_path: Path):
    aiwg = _prepare_aiwg(tmp_path)

    frame_builder = PromptFrameBuilder(aiwg_root=aiwg)
    frame = frame_builder.build_prompt_frame_for_phase(mission_id="m-pipeline", phase_id="P14", budget_limit=700, write_output=True)

    cache = PromptCacheLedger(aiwg_root=aiwg)
    cache.record_frame(frame)
    cache_summary = cache.summarize_cache(
        mission_id="m-pipeline",
        phase_id="P14",
        source_hash=frame.source_hash,
        receipt_ref=frame.receipt_ref,
        freshness_status="fresh",
        stale_report_path=aiwg / "reports" / "stale_memory_report.json",
        write_report=True,
    )
    assert "cache_hit_ratio" in cache_summary

    gate = RestartIntegrationGate(aiwg_root=aiwg)
    gate_result = gate.run_restart_gate(write_report=True)
    assert gate_result.decision in {"PASS", "PASS_WITH_WARNINGS"}

    benchmark = ContextEfficiencyBenchmark(aiwg_root=aiwg)
    bench_result = benchmark.run_context_efficiency_benchmark(write_report=True)
    assert len(bench_result.cases) == 3

    flywheel = EvolutionFlywheelRuntime(aiwg_root=aiwg)
    flywheel_result = flywheel.run_evolution_flywheel(write_report=True)
    assert flywheel_result.decision

    for rel in [
        "reports/prompt_frame_latest.json",
        "reports/prompt_cache_summary_latest.json",
        "reports/restart_integration_gate_latest.json",
        "reports/context_efficiency_benchmark_latest.json",
        "reports/evolution_flywheel_latest.json",
    ]:
        p = aiwg / rel
        assert p.exists()
        json.loads(p.read_text(encoding="utf-8"))
