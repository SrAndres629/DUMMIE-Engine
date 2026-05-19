import yaml
from pathlib import Path
from datetime import datetime, timezone
from layers.l2_brain.creator_context_runtime import CreatorContextRuntime
from layers.l2_brain.goal_reasoning_runtime import GoalReasoningRuntime
from layers.l2_brain.strategic_question_generator import StrategicQuestionGenerator
from layers.l2_brain.tool_opportunity_detector import ToolOpportunityDetector
from layers.l2_brain.revenue_goal_planner import RevenueGoalPlanner
from layers.l2_brain.business_advisor_runtime import BusinessAdvisorRuntime
from layers.l2_brain.business_goal_model import BusinessIntake

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
        # 1. Classify goal
        classification = self.goal_reasoning.classify_goal(goal_statement)
        
        # 2. Extract target mrr
        target_mrr = self.goal_reasoning.extract_target_mrr(goal_statement)
        
        # 3. Create business intake model
        intake = BusinessIntake(
            goal=goal_statement,
            target_mrr=target_mrr
        )
        
        # 4. Generate strategic questions
        questions = self.question_gen.generate_questions(goal_statement, classification.goal_type)
        
        # 5. Detect tool opportunities
        tools = self.tool_detector.detect_opportunities(goal_statement, classification.goal_type)
        
        # 6. Build roadmap plan
        roadmap = self.planner.build_roadmap(target_mrr, classification.goal_type)
        
        # 7. Generate business advice details
        advice_details = self.advisor.generate_advice(intake)
        
        # 8. Save goal memory entry
        self._record_goal(goal_statement, classification.goal_type)
        
        return {
            "creator_profile": {
                "name": self.creator_ctx.get_creator_name(),
                "preferred_name": self.creator_ctx.get_preferred_name(),
                "role": self.creator_ctx.get_creator_role()
            },
            "goal_classification": classification.to_dict(),
            "business_intake": intake.to_dict(),
            "strategic_questions": questions,
            "tool_opportunities": [t.to_dict() for t in tools],
            "roadmap": roadmap,
            "advice": advice_details
        }

    def _record_goal(self, goal: str, goal_type: str):
        goal_file = self.aiwg_root / "identity" / "goal_memory.yaml"
        try:
            if goal_file.exists():
                with open(goal_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            else:
                data = {}
            
            goals = data.get("goals", [])
            if not isinstance(goals, list):
                goals = []

            # Check for duplicate
            if not any(g.get("goal") == goal for g in goals if isinstance(g, dict)):
                goals.append({
                    "goal": goal,
                    "goal_type": goal_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "active"
                })
                data["goals"] = goals
                with open(goal_file, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
        except Exception:
            pass
