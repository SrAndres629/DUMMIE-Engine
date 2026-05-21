import json
from pathlib import Path

from layers.l2_brain.context.context_efficiency_benchmark import ContextEfficiencyBenchmark


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_inputs(tmp_path: Path, required_preserved: bool) -> Path:
    aiwg = tmp_path / ".aiwg"
    _write_json(
        aiwg / "reports" / "context_package_latest.json",
        {
            "items": [
                {"ref": "state:current_position", "estimated_tokens": 50, "required": True},
                {"ref": "wm:project_world_model", "estimated_tokens": 70, "required": True},
                {"ref": "note:f1", "estimated_tokens": 40, "required": False},
            ]
        },
    )
    kept = ["state:current_position", "wm:project_world_model"] if required_preserved else ["state:current_position"]
    _write_json(
        aiwg / "reports" / "context_quant_result_latest.json",
        {
            "estimated_total_tokens": 90,
            "kept_refs": kept,
            "dropped_refs": ["note:f1"],
            "compressed_refs": [],
        },
    )
    _write_json(aiwg / "reports" / "context_receipt_latest.json", {"decision": "WARN"})
    _write_json(aiwg / "reports" / "prompt_frame_latest.json", {"frame_id": "f1"})
    _write_json(aiwg / "reports" / "stale_memory_report.json", {"findings": []})
    _write_json(aiwg / "reports" / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.5, "reusable_frames": 1})
    _write_json(aiwg / "notes" / "folder_notes_manifest.json", {"folders": [{"folder_id": "f1"}]})
    return aiwg


def test_context_efficiency_benchmark_compares_three_strategies(tmp_path: Path):
    aiwg = _prepare_inputs(tmp_path, required_preserved=True)
    runner = ContextEfficiencyBenchmark(aiwg_root=aiwg)
    result = runner.run_context_efficiency_benchmark(write_report=True)

    assert len(result.cases) == 3
    names = {c.strategy for c in result.cases}
    assert names == {"raw_naive_estimate", "folder_notes_only", "quantized_context_frame"}
    assert (aiwg / "reports" / "context_efficiency_benchmark_latest.json").exists()


def test_quantized_cannot_claim_efficiency_if_required_context_lost(tmp_path: Path):
    aiwg = _prepare_inputs(tmp_path, required_preserved=False)
    runner = ContextEfficiencyBenchmark(aiwg_root=aiwg)
    result = runner.run_context_efficiency_benchmark(write_report=False)

    quant = next(c for c in result.cases if c.strategy == "quantized_context_frame")
    assert quant.required_context_preserved is False
    assert quant.expected_cloud_context_reduction_ratio == 0.0


def test_ratios_stay_between_zero_and_one(tmp_path: Path):
    aiwg = _prepare_inputs(tmp_path, required_preserved=True)
    runner = ContextEfficiencyBenchmark(aiwg_root=aiwg)
    result = runner.run_context_efficiency_benchmark(write_report=False)

    for case in result.cases:
        assert 0.0 <= case.expected_cloud_context_reduction_ratio <= 1.0
