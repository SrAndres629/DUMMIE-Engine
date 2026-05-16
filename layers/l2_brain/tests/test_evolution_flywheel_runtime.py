import json
from pathlib import Path

from layers.l2_brain.evolution_flywheel_runtime import EvolutionFlywheelRuntime


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_state(tmp_path: Path, gate_decision: str, benchmark_decision: str, quant_ratio: float) -> Path:
    aiwg = tmp_path / ".aiwg"

    _write_json(aiwg / "reports" / "restart_integration_gate_latest.json", {"decision": gate_decision})
    _write_json(
        aiwg / "reports" / "context_efficiency_benchmark_latest.json",
        {
            "decision": benchmark_decision,
            "summary": {"quantized_reduction_ratio": quant_ratio},
        },
    )
    _write_json(aiwg / "reports" / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.6, "reusable_frames": 2})
    _write_json(aiwg / "reports" / "stale_memory_report.json", {"findings": []})
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P17"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18"})
    return aiwg


def test_flywheel_continue_next_phase_on_good_signals(tmp_path: Path):
    aiwg = _prepare_state(tmp_path, gate_decision="PASS", benchmark_decision="IMPROVED", quant_ratio=0.25)
    runtime = EvolutionFlywheelRuntime(aiwg_root=aiwg)

    result = runtime.run_evolution_flywheel(write_report=True)
    assert result.decision == "continue_next_phase"
    assert result.recommended_next_phase == "P18"
    assert (aiwg / "reports" / "evolution_flywheel_latest.json").exists()


def test_flywheel_repair_before_next_phase_on_gate_fail(tmp_path: Path):
    aiwg = _prepare_state(tmp_path, gate_decision="FAIL", benchmark_decision="IMPROVED", quant_ratio=0.25)
    runtime = EvolutionFlywheelRuntime(aiwg_root=aiwg)

    result = runtime.run_evolution_flywheel(write_report=False)
    assert result.decision in {"repair_before_next_phase", "block_due_to_runtime_failure"}
    assert result.blocking_reasons
    assert result.expected_capability_gain
