"""End-to-end test for the full DUMMIE cognitive loop.

Proves that the entire chain works:
  raw prompt → PromptToMissionCompiler → SessionStore → EpistemicJudge
  → ColdPlanner → PatternMiner → PersonaGuardian
  → SelfWorktreeOrchestrator → next_loop proposal
"""

import json

import pytest

from prompt_to_mission import PromptToMissionCompiler
from session_store import SessionStore
from cognition.epistemic_judge import EpistemicJudge
from cognition.cold_planner import ColdPlanner
from cognition.pattern_miner import PatternMiner
from cognition.persona_guardian import PersonaGuardian
from self_worktree_orchestrator import SelfWorktreeOrchestrator


BLOCKED_NAMES = SelfWorktreeOrchestrator.BLOCKED_NAMES


class TestCognitiveLoopE2E:
    """Full cognitive loop integration test."""

    def test_prompt_to_next_loop_chain(self, tmp_path):
        """The entire cognitive chain produces a valid next_loop with no blocked paths."""

        # Step 1: PromptToMissionCompiler — raw prompt → structured mission
        compiler = PromptToMissionCompiler()
        mission = compiler.compile(
            {"prompt": "Harden epistemic judge and add contract-drift detection.", "authority_a": "HUMAN"}
        )

        assert mission["mission_id"].startswith("miss_")
        assert mission["goal"] == "Harden epistemic judge and add contract-drift detection."
        assert mission["authority_a"] == "HUMAN"
        assert "INTAKE" in mission["phases"]
        assert "NEXT_LOOP" in mission["phases"]
        assert "apply_patch" in mission["forbidden_actions"]

        # Step 2: SessionStore — create session and persist mission
        store = SessionStore(tmp_path)
        session_id = "e2e-cognitive-loop-001"
        session = store.create_session(session_id, metadata={"mission_id": mission["mission_id"]})
        assert session["state"]["session_id"] == session_id

        store.save_artifact(session_id, "intake.md", f"# Intake\n\nGoal: {mission['goal']}\n")
        store.append_event(session_id, "INTAKE", f"Mission compiled: {mission['mission_id']}")

        # Step 3: EpistemicJudge — classify claims
        judge = EpistemicJudge()

        supported = judge.evaluate_claim(
            "Epistemic judge correctly detects contradictions",
            [
                {"id": "test-ej-1", "type": "test", "supports": True, "summary": "test_higher_authority passes"},
            ],
        )
        assert supported["status"] == "SUPPORTED"
        assert supported["confidence"] == 1.0
        assert supported["decision"] == "trust"

        contradicted = judge.evaluate_claim(
            "Pattern miner handles all pattern types",
            [
                {"id": "spec-pm", "type": "active_spec", "supports": True},
                {"id": "code-pm", "type": "source_code", "contradicts": True, "summary": "Only 1 pattern type"},
            ],
        )
        assert contradicted["status"] == "CONTRADICTED"
        assert contradicted["decision"] == "reject"

        insufficient = judge.evaluate_claim("DUMMIE memory influences planning", [])
        assert insufficient["status"] == "INSUFFICIENT_EVIDENCE"

        store.save_artifact(
            session_id,
            "epistemic_check.md",
            f"# Epistemic Check\n\n- Supported: {supported['claim']}\n- Contradicted: {contradicted['claim']}\n- Insufficient: {insufficient['claim']}\n",
        )
        store.append_event(session_id, "EPISTEMIC_CHECK", "3 claims classified")

        # Step 4: ColdPlanner — rank candidate actions
        planner = ColdPlanner()
        candidates = [
            {
                "id": "fix_epistemic_bug",
                "rationale": "Fix dead code in epistemic judge.",
                "metrics": {
                    "impact_on_mvp": 0.8,
                    "risk_reduction": 0.9,
                    "unblock_future_loops": 0.7,
                    "testability": 1.0,
                    "implementation_cost_inverse": 0.9,
                    "reversibility": 1.0,
                },
                "paths": ["layers/l2_brain/cognition/epistemic_judge.py"],
                "required_tests": ["tests/test_epistemic_judge.py"],
            },
            {
                "id": "massive_rewrite",
                "rationale": "Rewrite entire cognition layer.",
                "metrics": {
                    "impact_on_mvp": 1.0,
                    "risk_reduction": 0.1,
                    "unblock_future_loops": 0.3,
                    "testability": 0.2,
                    "implementation_cost_inverse": 0.1,
                    "reversibility": 0.1,
                    "massive": 1.0,
                    "refactor": 1.0,
                },
                "paths": ["layers/l2_brain"],
            },
        ]
        selected = planner.select_next_action(candidates)
        assert selected["selected_action"] == "fix_epistemic_bug"
        assert selected["risk_level"] == "low"
        assert selected["score"] > 0.8

        store.append_event(session_id, "COLD_PLANNING", f"Selected: {selected['selected_action']}")

        # Step 5: PatternMiner — detect patterns from events
        miner = PatternMiner()
        historical_events = [
            {"id": "e1", "kind": "test_failure", "path": "layers/l2_brain/cognition/epistemic_judge.py"},
            {"id": "e2", "kind": "test_failure", "path": "layers/l2_brain/cognition/epistemic_judge.py"},
            {"id": "e3", "kind": "test_failure", "path": "layers/l2_brain/cognition/epistemic_judge.py"},
            {"id": "drift-spec", "path": "layers/l2_brain/daemon.py", "type": "active_spec", "supports": True},
            {"id": "drift-code", "path": "layers/l2_brain/daemon.py", "type": "source_code", "contradicts": True},
        ]
        patterns = miner.mine_patterns(historical_events)
        assert len(patterns) >= 1
        hotspots = [p for p in patterns if p["name"] == "Repeated event hotspot"]
        drifts = [p for p in patterns if p["name"] == "Contract drift"]
        assert len(hotspots) == 1
        assert len(drifts) == 1

        store.append_event(session_id, "PATTERN_MINING", f"Detected {len(patterns)} patterns")

        # Step 6: PersonaGuardian — alignment check
        guardian = PersonaGuardian()
        alignment = guardian.evaluate_alignment({
            "mission_alignment": 0.9,
            "scientific_rigor": 0.85,
            "engineering_robustness": 0.9,
            "memory_improvement": 0.7,
            "business_utility": 0.6,
            "risk_of_narrative_bloat": 0.15,
        })
        assert alignment["decision"] == "approve"

        store.append_event(session_id, "PERSONA_CHECK", f"Alignment: {alignment['decision']}")

        # Step 7: SelfWorktreeOrchestrator — full loop
        orchestrator = SelfWorktreeOrchestrator(tmp_path)
        orch_session_id = "e2e-orch-001"
        orchestrator.start_self_session(orch_session_id, prompt=mission["goal"])

        context = orchestrator.load_global_context(orch_session_id)
        assert "artifact" in context

        assessment = orchestrator.assess_repo(orch_session_id)
        assert assessment["status"] in {"OK", "NO_INVENTORY"}

        patch_plan = orchestrator.plan_safe_patch(
            orch_session_id,
            mission["goal"],
            candidate_paths=["layers/l2_brain/cognition/epistemic_judge.py"],
        )
        assert patch_plan["apply_patch_enabled"] is False
        assert "layers/l2_brain/cognition/epistemic_judge.py" in patch_plan["allowed_paths"]
        # Verify no blocked path leaked through
        for blocked in BLOCKED_NAMES:
            assert blocked not in patch_plan["allowed_paths"]

        result = orchestrator.record_patch_result(
            orch_session_id, patch_plan["plan_id"], "validated", ["pytest"]
        )
        assert result["status"] == "validated"

        next_loop = orchestrator.propose_next_loop(orch_session_id)
        assert next_loop["artifact"] == "next_loop.md"
        assert next_loop["events_observed"] > 0

        # Step 8: Verify session artifacts completeness
        loaded = orchestrator.store.load_session(orch_session_id)
        required_artifacts = {
            "intake.md",
            "global_recall.md",
            "epistemic_check.md",
            "cold_plan.md",
            "research_tree.md",
            "patch_plan.md",
            "validation_report.md",
            "next_loop.md",
        }
        assert required_artifacts.issubset(set(loaded["artifacts"]))

        # Step 9: Verify full output is JSON-serializable
        full_output = {
            "mission": mission,
            "epistemic_results": [supported, contradicted, insufficient],
            "selected_action": selected,
            "patterns": patterns,
            "persona_alignment": alignment,
            "patch_plan": patch_plan,
            "next_loop": next_loop,
        }
        serialized = json.dumps(full_output, default=str)
        assert isinstance(serialized, str)
        assert len(serialized) > 100

    def test_blocked_paths_never_appear_in_allowed(self, tmp_path):
        """No blocked path can be selected in the cognitive loop."""
        orchestrator = SelfWorktreeOrchestrator(tmp_path)
        orchestrator.start_self_session("blocked-test")

        for blocked in [".env", ".git/config", "uv.lock", "package-lock.json", "../escape"]:
            with pytest.raises(ValueError):
                orchestrator.plan_safe_patch("blocked-test", "test", candidate_paths=[blocked])

    def test_destructive_prompt_rejected_at_intake(self):
        """Destructive prompts are blocked before the chain starts."""
        compiler = PromptToMissionCompiler()

        with pytest.raises(ValueError):
            compiler.compile("rm -rf / and rebuild")

        with pytest.raises(ValueError):
            compiler.compile("delete .git history")

    def test_empty_prompt_rejected(self):
        """Empty prompts are rejected."""
        compiler = PromptToMissionCompiler()

        with pytest.raises(ValueError):
            compiler.compile("")
