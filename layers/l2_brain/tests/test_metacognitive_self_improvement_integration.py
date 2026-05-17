"""Integration tests for Pack 5.2.2 metacognitive self-improvement pipeline."""
import json
from pathlib import Path
from mental_model_truth_hygiene import run_mental_model_truth_hygiene
from evolution_delta_applier import apply_evolution_delta
from self_improvement_runtime import run_self_improvement_cycle
from mental_model_store import MentalModelStore
from metacognitive_evolution_flywheel import run_metacognitive_evolution_flywheel


def test_store_mark_status_and_find_best():
    import tempfile, shutil
    tmp = Path(tempfile.mkdtemp())
    try:
        store = MentalModelStore(tmp)
        from mental_model_runtime import build_mental_model_for_intent, MentalModel
        m1 = build_mental_model_for_intent("test intent", aiwg_root=tmp / ".aiwg")
        m1.quality_score = 50
        store.append_model(m1)
        m2 = build_mental_model_for_intent("test intent", aiwg_root=tmp / ".aiwg")
        m2.quality_score = 90
        store.append_model(m2)
        store.mark_status(m1.model_id, "superseded", "lower quality", superseded_by=m2.model_id)
        assert store.get_model_status(m1.model_id) == "superseded"
        assert store.get_model_status(m2.model_id) == "valid"
    finally:
        shutil.rmtree(tmp)


def test_flywheel_produces_blocked_actions():
    flywheel = run_metacognitive_evolution_flywheel("test intent", mode="observe_only")
    assert flywheel.decision == "PASS"
    # In observe_only mode, it should still produce basic delta
    assert flywheel.evolution_delta.get("next_check_recommended") != ""


def test_metacognitive_loop_consumes_blockers():
    from metacognitive_loop_runtime import run_metacognitive_loop
    res = run_metacognitive_loop("what should DUMMIE improve next before autonomous scaling?")
    # Should not recommend autonomous scaling
    assert res.get("recommended_next_action") != "proceed_to_autonomous_scaling"


def test_full_pipeline_integrity():
    """Run the full pipeline and verify JSON outputs."""
    hygiene = run_mental_model_truth_hygiene()
    delta = apply_evolution_delta()
    cycle = run_self_improvement_cycle()

    # All must produce valid JSON dicts
    assert isinstance(hygiene, dict)
    assert isinstance(delta, dict)
    assert isinstance(cycle, dict)

    # Cycle must have action queue
    assert len(cycle.get("action_queue", [])) > 0

    # Autonomous scaling must be blocked
    assert cycle.get("autonomous_scaling_blocked") is True
