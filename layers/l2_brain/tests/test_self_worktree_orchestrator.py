import pytest

from self_worktree_orchestrator import SelfWorktreeOrchestrator


def test_self_orchestrator_creates_plan_only_runtime_artifacts(tmp_path):
    orchestrator = SelfWorktreeOrchestrator(tmp_path)

    session = orchestrator.start_self_session("self-1", prompt="Improve owned modules")
    assert session["state"]["session_type"] == "self_worktree"

    context = orchestrator.load_global_context("self-1")
    assessment = orchestrator.assess_repo("self-1")
    patch_plan = orchestrator.plan_safe_patch(
        "self-1",
        "Add tests",
        candidate_paths=["layers/l2_brain/session_store.py"],
    )
    result = orchestrator.record_patch_result("self-1", patch_plan["plan_id"], "validated", ["pytest"])
    next_loop = orchestrator.propose_next_loop("self-1")

    assert "global_recall.md" in context["artifact"]
    assert assessment["status"] in {"OK", "NO_INVENTORY"}
    assert patch_plan["apply_patch_enabled"] is False
    assert patch_plan["allowed_paths"] == ["layers/l2_brain/session_store.py"]
    assert result["status"] == "validated"
    assert next_loop["artifact"] == "next_loop.md"

    loaded = orchestrator.store.load_session("self-1")
    expected = {
        "intake.md",
        "global_recall.md",
        "epistemic_check.md",
        "cold_plan.md",
        "research_tree.md",
        "swarm_debate.md",
        "patch_plan.md",
        "validation_report.md",
        "decision_log.md",
        "lessons_learned.md",
        "next_loop.md",
    }
    assert expected.issubset(set(loaded["artifacts"]))


@pytest.mark.parametrize(
    "blocked",
    [".env", ".git/config", "uv.lock", "package-lock.json", "dist/generated.py", "../outside.py"],
)
def test_self_orchestrator_rejects_blocked_patch_paths(tmp_path, blocked):
    orchestrator = SelfWorktreeOrchestrator(tmp_path)
    orchestrator.start_self_session("self-1")

    with pytest.raises(ValueError):
        orchestrator.plan_safe_patch("self-1", "Unsafe", candidate_paths=[blocked])
