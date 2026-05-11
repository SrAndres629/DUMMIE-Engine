import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("dummie.brain.vault")

class VaultCurator:
    """
    [L2_BRAIN] Crystallizes temporary mission artifacts into permanent knowledge.
    Ensures that "Golden Paths" and lessons are preserved and searchable.
    """
    def __init__(self, vault_path: str = ".aiwg/vault"):
        self.vault_path = os.path.abspath(vault_path)
        os.makedirs(self.vault_path, exist_ok=True)

    def extract_vault_entries(self, mission_id: str, workbench_path: str) -> List[Dict[str, Any]]:
        """
        Scans a workbench for candidates to promote to the vault.
        """
        candidates = []
        
        # 1. Load manifest and outcome
        manifest_path = os.path.join(workbench_path, "manifest.json")
        outcome_path = os.path.join(workbench_path, "outcome_metrics.json")
        
        if not os.path.exists(manifest_path) or not os.path.exists(outcome_path):
            return []
            
        with open(outcome_path, "r") as f:
            outcome = json.load(f)
            
        # 2. Only promote 'Golden Paths' for successful missions
        if outcome.get("status") == "SUCCESS":
            summary_path = os.path.join(workbench_path, "final_summary.md")
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    content = f.read()
                
                candidates.append({
                    "vault_id": f"gp-{uuid.uuid4().hex[:8]}",
                    "mission_id": mission_id,
                    "entry_type": "golden_path",
                    "summary": f"Successful execution of: {outcome.get('goal', 'unknown mission')}",
                    "content": {"markdown": content},
                    "evidence_refs": [os.path.join(workbench_path, "outcome_metrics.json")],
                    "created_at": datetime.now().isoformat()
                })
        
        # 3. Always look for failed patterns to avoid repetition
        if outcome.get("status") == "FAILED":
            candidates.append({
                "vault_id": f"fp-{uuid.uuid4().hex[:8]}",
                "mission_id": mission_id,
                "entry_type": "failed_pattern",
                "summary": f"Failure analysis for: {outcome.get('error', 'unknown error')}",
                "content": {"error": outcome.get("error"), "stack": outcome.get("stack")},
                "created_at": datetime.now().isoformat()
            })
            
        return candidates

    def store_vault_entry(self, entry: Dict[str, Any]) -> str:
        """
        Persists a vault entry to disk.
        """
        # Security: Strip potential secrets (heuristic)
        entry_str = json.dumps(entry)
        for sensitive in ["api_key", "password", "token", "secret"]:
            if sensitive in entry_str.lower():
                raise ValueError(f"Security Violation: Vault entry contains sensitive term: {sensitive}")
        
        filename = f"{entry['vault_id']}.json"
        target_path = os.path.join(self.vault_path, filename)
        
        with open(target_path, "w") as f:
            json.dump(entry, f, indent=2)
            
        return target_path

    def finalize_and_clean(self, mission_id: str, workbench_path: str) -> Dict[str, Any]:
        """
        Executes the promotion pipeline and returns summary stats.
        """
        candidates = self.extract_vault_entries(mission_id, workbench_path)
        stored_paths = []
        
        for cand in candidates:
            try:
                path = self.store_vault_entry(cand)
                stored_paths.append(path)
            except Exception as e:
                logger.error(f"Failed to store vault entry {cand.get('vault_id')}: {e}")
                
        return {
            "mission_id": mission_id,
            "entries_promoted": len(stored_paths),
            "stored_paths": stored_paths
        }
