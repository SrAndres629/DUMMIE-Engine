import logging
from .contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.deliberation_hooks")

class MissionDecomposerHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        if frame.refined_intent == "OBJECTIVE_AUTOMATION":
            frame.mission_plan = [
                {"step": 1, "agent": "ResearchAgent", "action": "Investigate tools and APIs"},
                {"step": 2, "agent": "BuilderAgent", "action": "Create automation scripts"},
                {"step": 3, "agent": "QA_Agent", "action": "Verify scripts and safety"},
                {"step": 4, "agent": "HumanLiaison", "action": "Request final approval"},
            ]
        else:
            frame.mission_plan = [
                {"step": 1, "agent": "ObserverAgent", "action": "Analyze current state"},
            ]
        return frame

class PlanCriticHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        # Self-critique logic
        if not frame.mission_plan:
            frame.deliberation_summary = "CRITIQUE: Mission plan is empty. Fallback required."
        else:
            frame.deliberation_summary = f"CRITIQUE: Plan with {len(frame.mission_plan)} steps accepted."
        return frame
