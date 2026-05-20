from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from layers.l2_brain.business_advisor_runtime import BusinessAdvisorRuntime
from layers.l2_brain.business_goal_model import BusinessIntake
from layers.l2_brain.creator_context_runtime import CreatorContextRuntime
from layers.l2_brain.goal_reasoning_runtime import GoalReasoningRuntime
from layers.l2_brain.revenue_goal_planner import RevenueGoalPlanner
from layers.l2_brain.strategic_question_generator import StrategicQuestionGenerator
from layers.l2_brain.tool_opportunity_detector import ToolOpportunityDetector


class StrategicPartnerRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.creator_ctx = CreatorContextRuntime(self.aiwg_root)
        self.goal_reasoning = GoalReasoningRuntime()
        self.question_gen = StrategicQuestionGenerator()
        self.tool_detector = ToolOpportunityDetector()
        self.planner = RevenueGoalPlanner()
        self.advisor = BusinessAdvisorRuntime(self.aiwg_root)

    def advise(self, goal_statement: str) -> dict:
        classification = self.goal_reasoning.classify_goal(goal_statement)
        target_mrr = self.goal_reasoning.extract_target_mrr(goal_statement)

        intake = BusinessIntake(goal=goal_statement, target_mrr=target_mrr)

        questions = self.question_gen.generate_questions(goal_statement, classification.goal_type)
        tools = self.tool_detector.detect_opportunities(goal_statement, classification.goal_type)
        roadmap = self.planner.build_roadmap(target_mrr, classification.goal_type)
        advice_details = self.advisor.generate_advice(intake)

        self._record_goal(goal_statement, classification.goal_type)

        return {
            "creator_profile": {
                "name": self.creator_ctx.get_creator_name(),
                "preferred_name": self.creator_ctx.get_preferred_name(),
                "role": self.creator_ctx.get_creator_role(),
            },
            "goal_classification": classification.to_dict(),
            "business_intake": intake.to_dict(),
            "strategic_questions": questions,
            "tool_opportunities": [t.to_dict() for t in tools],
            "roadmap": roadmap,
            "advice": advice_details,
        }

    def _record_goal(self, goal: str, goal_type: str) -> None:
        goal_file = self.aiwg_root / "identity" / "goal_memory.yaml"
        goal_file.parent.mkdir(parents=True, exist_ok=True)

        if goal_file.exists():
            loaded = yaml.safe_load(goal_file.read_text(encoding="utf-8")) or {}
            data = loaded if isinstance(loaded, dict) else {}
        else:
            data = {}

        goals = data.get("goals", [])
        if not isinstance(goals, list):
            goals = []

        already_exists = any(
            isinstance(item, dict)
            and item.get("goal") == goal
            and item.get("goal_type") == goal_type
            for item in goals
        )
        if already_exists:
            return

        goals.append(
            {
                "goal": goal,
                "goal_type": goal_type,
                "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "status": "active",
            }
        )
        data["goals"] = goals
        goal_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
