import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("dummie.brain.workbench")

class MissionWorkbenchManager:
    """
    [L2_BRAIN] Manages the physical workspace for every mission.
    Ensures structured persistence of reasoning artifacts.
    """
    def __init__(self, base_path: str = ".aiwg/workbench"):
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)

    def _get_mission_path(self, mission_id: str) -> str:
        # Prevent path traversal
        safe_id = "".join(c for c in mission_id if c.isalnum() or c in ("-", "_"))
        target_path = os.path.abspath(os.path.join(self.base_path, safe_id))
        
        if not target_path.startswith(self.base_path):
            raise ValueError(f"Security Violation: Attempted path traversal for mission {mission_id}")
        
        return target_path

    def create_workbench(self, mission_id: str, session_id: str, user_goal: str) -> Dict[str, Any]:
        path = self._get_mission_path(mission_id)
        os.makedirs(path, exist_ok=True)
        
        manifest = {
            "mission_id": mission_id,
            "session_id": session_id,
            "user_goal": user_goal,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "artifacts": []
        }
        
        manifest_path = os.path.join(path, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        self.write_artifact(mission_id, "objective.md", f"# Mission Objective\n\n{user_goal}", "markdown")
        
        return manifest

    def write_artifact(self, mission_id: str, name: str, content: str, kind: str) -> Dict[str, Any]:
        path = self._get_mission_path(mission_id)
        
        # Ensure name is safe and doesn't contain separators
        if "/" in name or "\\" in name:
            raise ValueError(f"Security Violation: Artifact name {name} contains directory separators")
            
        if name.startswith(".") or ".env" in name.lower():
            raise ValueError(f"Security Violation: Invalid artifact name {name}")
            
        artifact_path = os.path.join(path, name)
        
        with open(artifact_path, "w") as f:
            f.write(content)
            
        return {"name": name, "path": artifact_path, "kind": kind}

    def append_decision(self, mission_id: str, decision_event: Dict[str, Any]):
        path = self._get_mission_path(mission_id)
        log_path = os.path.join(path, "decision_log.jsonl")
        
        # Security check: Remove potential CoT
        clean_event = {k: v for k, v in decision_event.items() if "thought" not in k.lower() and "monologue" not in k.lower()}
        clean_event["timestamp"] = datetime.now().isoformat()
        
        with open(log_path, "a") as f:
            f.write(json.dumps(clean_event) + "\n")

    def finalize_workbench(self, mission_id: str, outcome: Dict[str, Any]) -> Dict[str, Any]:
        path = self._get_mission_path(mission_id)
        
        self.write_artifact(mission_id, "outcome_metrics.json", json.dumps(outcome, indent=2), "json")
        
        summary = f"# Mission Summary\n\nStatus: {outcome.get('status', 'unknown')}\n"
        summary += f"Finalized at: {datetime.now().isoformat()}\n\n"
        summary += "## Results\n"
        summary += outcome.get("error", "No errors reported.")
        
        self.write_artifact(mission_id, "final_summary.md", summary, "markdown")
        
        # Update manifest
        manifest_path = os.path.join(path, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            manifest["status"] = "finalized"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
                
        return {"mission_id": mission_id, "path": path, "status": "finalized"}
