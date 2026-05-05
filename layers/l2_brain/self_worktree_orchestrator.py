import os
from pathlib import Path
from typing import Any

try:
    from session_store import SessionStore
except ImportError:  # pragma: no cover - package import fallback
    from layers.l2_brain.session_store import SessionStore

try:
    from cognition.epistemic_judge import EpistemicJudge
    from cognition.cold_planner import ColdPlanner
    from cognition.pattern_miner import PatternMiner
    from cognition.persona_guardian import PersonaGuardian
except ImportError:  # pragma: no cover - package import fallback
    from layers.l2_brain.cognition.epistemic_judge import EpistemicJudge
    from layers.l2_brain.cognition.cold_planner import ColdPlanner
    from layers.l2_brain.cognition.pattern_miner import PatternMiner
    from layers.l2_brain.cognition.persona_guardian import PersonaGuardian


class SelfWorktreeOrchestrator:
    BLOCKED_NAMES = {
        ".env",
        ".git",
        "uv.lock",
        "poetry.lock",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Pipfile.lock",
        "Cargo.lock",
    }
    GENERATED_PARTS = {"dist", "build", "__pycache__", ".pytest_cache", "generated"}
    GENERATED_SUFFIXES = {".pyc", ".pyo"}

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir).resolve()
        self.store = SessionStore(self.root_dir)
        self.judge = EpistemicJudge()
        self.planner = ColdPlanner()
        self.pattern_miner = PatternMiner()
        self.persona_guardian = PersonaGuardian()

    def start_self_session(self, session_id: str, prompt: str = "") -> dict[str, Any]:
        session = self.store.create_session(
            session_id,
            metadata={"session_type": "self_worktree", "patch_application_enabled": False},
        )
        content = "\n".join(
            [
                "# Intake",
                "",
                f"Session: {session_id}",
                f"Prompt: {prompt or 'No prompt provided.'}",
                "Mode: plan-only",
                "",
            ]
        )
        self.store.save_artifact(session_id, "intake.md", content)
        self.store.append_event(session_id, "INTAKE", "Started plan-only self worktree session.")
        return self.store.load_session(session_id)

    def assess_repo(self, session_id: str | None = None) -> dict[str, Any] | str:
        inventory_path = self.root_dir / ".aiwg" / "index" / "repo_inventory.jsonl"
        if inventory_path.exists():
            lines = inventory_path.read_text(encoding="utf-8").splitlines()
            status = "OK"
            summary = f"Repo assess: {len(lines)} files detected."
            evidence = [{"type": "source_code", "ref": str(inventory_path)}]
        else:
            lines = []
            status = "NO_INVENTORY"
            summary = "Repository inventory not found."
            evidence = []

        assessment = self.judge.evaluate_claim(summary, evidence)
        result = {"status": status, "files_detected": len(lines), "summary": summary, "epistemic_check": assessment}
        if session_id is None:
            return summary

        self.store.save_artifact(
            session_id,
            "epistemic_check.md",
            f"# Epistemic Check\n\n{summary}\n\nDecision: {assessment['decision']}\n",
        )
        self.store.append_event(session_id, "EPISTEMIC_CHECK", summary, evidence_refs=[str(inventory_path)])
        return result

    def load_global_context(self, session_id: str) -> dict[str, Any]:
        context_files = [
            self.root_dir / ".aiwg" / "README.md",
            self.root_dir / ".aiwg" / "control" / "REASONING_PROTOCOL.md",
            self.root_dir / ".aiwg" / "control" / "WORKTREE_RULES.yaml",
        ]
        found = [str(path.relative_to(self.root_dir)) for path in context_files if path.exists()]
        body = "# Global Recall\n\n" + "\n".join(f"- {path}" for path in found)
        if not found:
            body += "- No global context files found."
        body += "\n"
        self.store.save_artifact(session_id, "global_recall.md", body)
        self.store.append_event(session_id, "GLOBAL_RECALL", f"Loaded {len(found)} global context files.", evidence_refs=found)
        return {"artifact": "global_recall.md", "context_refs": found}

    def plan_safe_patch(
        self,
        session_id: str,
        goal: str,
        candidate_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        candidate_paths = candidate_paths or []
        allowed_paths = [self._validate_patch_path(path) for path in candidate_paths]

        candidates = [
            {
                "id": "plan_patch",
                "rationale": goal,
                "paths": allowed_paths,
                "metrics": {
                    "impact_on_mvp": 0.7,
                    "risk_reduction": 0.7,
                    "unblock_future_loops": 0.6,
                    "testability": 0.8,
                    "implementation_cost_inverse": 0.6,
                    "reversibility": 0.9,
                },
            }
        ]
        selected = self.planner.select_next_action(candidates)
        patterns = self.pattern_miner.mine_patterns(self.store.load_session(session_id)["events"])
        alignment = self.persona_guardian.evaluate_alignment(
            {"metrics": {"scientific_rigor": 0.8, "risk_of_bloat": 0.2}}
        )
        plan = {
            "plan_id": f"plan_{self.store.load_session(session_id)['state'].get('lamport_t', 0) + 1}",
            "goal": goal,
            "apply_patch_enabled": False,
            "allowed_paths": allowed_paths,
            "blocked_paths": sorted(self.BLOCKED_NAMES),
            "selected_action": selected,
            "patterns": patterns,
            "persona_alignment": alignment,
        }
        self.store.save_artifact(session_id, "cold_plan.md", self._render_cold_plan(plan))
        self.store.save_artifact(session_id, "research_tree.md", self._render_research_tree(goal))
        self.store.save_artifact(session_id, "swarm_debate.md", self._render_swarm_debate(plan))
        self.store.save_artifact(session_id, "patch_plan.md", self._render_patch_plan(plan))
        self.store.save_artifact(session_id, "decision_log.md", self._render_decision_log(plan))
        self.store.append_event(session_id, "PATCH_PLAN", f"Planned safe patch for: {goal}", data=plan)
        return plan

    def record_patch_result(
        self,
        session_id: str,
        plan_id: str,
        status: str,
        validation_evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        result = {
            "plan_id": plan_id,
            "status": status,
            "validation_evidence": validation_evidence or [],
            "patch_application_enabled": False,
        }
        self.store.save_artifact(
            session_id,
            "validation_report.md",
            self._render_validation_report(result),
        )
        self.store.save_artifact(
            session_id,
            "lessons_learned.md",
            self._render_lessons_learned(result),
        )
        self.store.append_event(
            session_id,
            "VALIDATION",
            f"Recorded patch plan result: {status}",
            data=result,
            evidence_refs=result["validation_evidence"],
        )
        return result

    def propose_next_loop(self, session_id: str) -> dict[str, Any]:
        loaded = self.store.load_session(session_id)
        next_loop = {
            "artifact": "next_loop.md",
            "session_id": session_id,
            "events_observed": len(loaded["events"]),
            "recommended_focus": "Validate current patch plan, then commit memory before execution.",
        }
        self.store.save_artifact(
            session_id,
            "next_loop.md",
            "# Next Loop\n\n- Validate planned changes.\n- Keep patch application disabled.\n- Commit memory after verification.\n",
        )
        self.store.append_event(session_id, "NEXT_LOOP", "Proposed next runtime loop.", data=next_loop)
        return next_loop

    def _validate_patch_path(self, raw_path: str) -> str:
        path = Path(raw_path)
        if path.is_absolute() or ".." in path.parts or not raw_path:
            raise ValueError(f"Blocked patch path: {raw_path}")
        if any(part in self.BLOCKED_NAMES for part in path.parts):
            raise ValueError(f"Blocked patch path: {raw_path}")
        if any(part in self.GENERATED_PARTS for part in path.parts):
            raise ValueError(f"Blocked generated path: {raw_path}")
        if path.suffix in self.GENERATED_SUFFIXES:
            raise ValueError(f"Blocked generated path: {raw_path}")
        resolved = (self.root_dir / path).resolve()
        try:
            resolved.relative_to(self.root_dir)
        except ValueError as exc:
            raise ValueError(f"Blocked patch path: {raw_path}") from exc
        return path.as_posix()

    @staticmethod
    def _render_cold_plan(plan: dict[str, Any]) -> str:
        return f"# Cold Plan\n\nGoal: {plan['goal']}\n\nApply patch enabled: false\n"

    @staticmethod
    def _render_research_tree(goal: str) -> str:
        return f"# Research Tree\n\n- Goal: {goal}\n- Evidence before edits.\n- Validation before memory commit.\n"

    @staticmethod
    def _render_patch_plan(plan: dict[str, Any]) -> str:
        paths = "\n".join(f"- {path}" for path in plan["allowed_paths"]) or "- No paths selected."
        return f"# Patch Plan\n\nPlan: {plan['plan_id']}\n\nAllowed paths:\n{paths}\n\nApply patch enabled: false\n"

    @staticmethod
    def _render_swarm_debate(plan: dict[str, Any]) -> str:
        return "\n".join(
            [
                "# Swarm Debate",
                "",
                f"Goal: {plan['goal']}",
                "",
                "- Architect: keep boundary explicit.",
                "- Builder: implement only after validation plan exists.",
                "- Validator: require evidence before success claims.",
                "- Integrator: keep patch application disabled in MVP.",
                "",
            ]
        )

    @staticmethod
    def _render_decision_log(plan: dict[str, Any]) -> str:
        return "\n".join(
            [
                "# Decision Log",
                "",
                f"Decision: create plan-only patch plan {plan['plan_id']}.",
                "Confidence: medium",
                "Rejected options: direct patch execution, destructive paths, generated artifacts.",
                "Rollback: discard session artifacts or create a new session.",
                "Validation: run required tests before memory commit.",
                "",
            ]
        )

    @staticmethod
    def _render_validation_report(result: dict[str, Any]) -> str:
        evidence = "\n".join(f"- {item}" for item in result["validation_evidence"]) or "- No validation evidence recorded."
        return f"# Validation Report\n\nStatus: {result['status']}\n\nEvidence:\n{evidence}\n"

    @staticmethod
    def _render_lessons_learned(result: dict[str, Any]) -> str:
        return "\n".join(
            [
                "# Lessons Learned",
                "",
                f"- Patch result status: {result['status']}.",
                "- Keep self-worktree orchestration plan-only until validator evidence is present.",
                "",
            ]
        )
