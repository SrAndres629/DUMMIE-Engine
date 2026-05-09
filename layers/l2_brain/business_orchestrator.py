from pathlib import Path
from typing import Any

try:
    from prompt_to_mission import PromptToMissionCompiler
    from session_store import SessionStore
except ImportError:  # pragma: no cover - package import fallback
    from layers.l2_brain.prompt_to_mission import PromptToMissionCompiler
    from layers.l2_brain.session_store import SessionStore


class BusinessSolutionOrchestrator:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir).resolve()
        self.store = SessionStore(self.root_dir)
        self.compiler = PromptToMissionCompiler()

    def start_business_session(self, session_id: str, mission_input: str | dict[str, Any]) -> dict[str, Any]:
        mission = self.compiler.compile(mission_input)
        self.store.create_session(
            session_id,
            metadata={
                "session_type": "business_solution",
                "mission_id": mission["mission_id"],
                "goal": mission["goal"],
            },
        )
        self.store.save_artifact(session_id, "business_brief.md", self._business_brief(mission))
        self.store.append_event(session_id, "INTAKE", "Started business solution session.", data={"mission": mission})
        return self.store.load_session(session_id)

    def create_solution_package(
        self,
        session_id: str,
        market: str = "unspecified",
        users: list[str] | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        goal = session["state"].get("goal", "Business solution")
        mission_id = session["state"].get("mission_id", "")
        mission = {"mission_id": mission_id, "goal": goal}
        users = users or []

        artifacts = {
            "prd.md": self._prd(goal, market, users),
            "architecture.md": self._architecture(goal),
            "backlog.md": self._backlog(goal),
            "validation_plan.md": self._validation_plan(market, users),
            "risk_register.md": self._risk_register(),
        }
        for name, content in artifacts.items():
            self.store.save_artifact(session_id, name, content)
        self.store.append_event(session_id, "COLD_PLANNING", "Created business solution package.")
        return {"mission": mission, "artifacts": sorted(artifacts)}

    def propose_next_loop(self, session_id: str) -> dict[str, Any]:
        next_loop = {
            "artifact": "next_loop.md",
            "recommended_focus": "Validate PRD assumptions and prioritize the first backlog slice.",
        }
        self.store.save_artifact(
            session_id,
            "next_loop.md",
            "# Next Loop\n\n- Validate the target user and buying trigger.\n- Select the smallest shippable backlog item.\n",
        )
        self.store.append_event(session_id, "NEXT_LOOP", "Proposed business next loop.", data=next_loop)
        return next_loop

    @staticmethod
    def _business_brief(mission: dict[str, Any]) -> str:
        return f"# Business Brief\n\nMission: {mission['mission_id']}\n\nGoal: {mission['goal']}\n"

    @staticmethod
    def _prd(goal: str, market: str, users: list[str]) -> str:
        user_lines = "\n".join(f"- {user}" for user in users) or "- Unspecified"
        return f"# PRD\n\nGoal: {goal}\n\nMarket: {market}\n\nUsers:\n{user_lines}\n"

    @staticmethod
    def _architecture(goal: str) -> str:
        return f"# Architecture\n\nPlan a modular MVP for: {goal}\n\n- Session runtime\n- Artifact store\n- Validation loop\n"

    @staticmethod
    def _backlog(goal: str) -> str:
        return f"# Backlog\n\n- Capture problem statement for {goal}\n- Define acceptance tests\n- Validate MVP slice\n"

    @staticmethod
    def _validation_plan(market: str, users: list[str]) -> str:
        return f"# Validation Plan\n\nMarket: {market}\n\n- Interview target users: {len(users)} listed\n- Verify willingness to adopt\n"

    @staticmethod
    def _risk_register() -> str:
        return "# Risk Register\n\n- Scope creep: keep MVP artifacts small.\n- Evidence gaps: require validation before next loop.\n"
