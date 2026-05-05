from typing import Any, Dict
from patch_transaction import PatchProposal

class SelfHealingPlanner:
    def __init__(self, mcp_gateway: Any):
        self.mcp_gateway = mcp_gateway

    async def generate_patch_proposal(self, mission: Dict[str, Any], context: Dict[str, Any] = None) -> PatchProposal:
        """
        Takes a mission and proposes a real PatchProposal.
        """
        mission_id = mission.get("mission_id", "miss-unknown")
        source_pattern_id = mission.get("source_pattern_id", "pattern-unknown")
        
        # Extract metadata from mission
        # In a real scenario, we'd use LLM/Reasoning to determine these.
        # For now, we use a robust structural bridge.
        
        goal = mission.get("goal", "")
        
        # Simulation of a repair plan
        affected_paths = mission.get("context_refs", []) or ["src/unspecified_fix.py"]
        
        # Standard safety gates from the mission compiler
        gates = mission.get("self_healing_safety_gates", {
            "apply_patch_enabled": False,
            "persona_guardian_required": True,
            "requires_human_approval": True
        })
        
        proposal = PatchProposal(
            proposal_id=f"prop-{mission_id}",
            source_pattern_id=source_pattern_id,
            mission_id=mission_id,
            affected_paths=affected_paths,
            diff_unified=f"--- {affected_paths[0]}\n+++ {affected_paths[0]}\n+ # Auto-fix for {goal}",
            tests_to_run=["pytest layers/l2_brain/tests/test_preflight.py"],
            rollback_plan=f"git checkout {affected_paths[0]}",
            safety_gates=gates
        )
        
        return proposal
