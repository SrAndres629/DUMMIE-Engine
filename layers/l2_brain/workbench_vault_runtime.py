from __future__ import annotations

import logging
import uuid
from typing import Any

from layers.l2_brain.learning_episode import LearningEpisode

logger = logging.getLogger(__name__)


class WorkbenchVaultRuntime:
    """
    [L2_BRAIN] Workbench & Vault Runtime Coordinator.
    Orchestrates the lifecycle between mission-specific workspaces and the global knowledge vault.
    """

    def __init__(
        self,
        workbench_manager: Any,
        vault_curator: Any,
        phase_ledger: Any = None,
        session_store: Any = None,
    ):
        self.workbench_manager = workbench_manager
        self.vault_curator = vault_curator
        self.phase_ledger = phase_ledger
        self.session_store = session_store

    def create_for_mission(self, mission_id: str, user_goal: str, phase_id: str = "") -> dict:
        """Create a new workbench for a mission and record it in the ledger."""
        meta = self.workbench_manager.create_workbench(mission_id, user_goal, phase_id)
        if self.phase_ledger:
             self.phase_ledger.append_event(mission_id, {
                 "event_type": "WORKBENCH_CREATED",
                 "phase_id": phase_id,
                 "workbench_ref": meta.get("workbench_ref"),
             })
        return meta

    def append_decision(self, mission_id: str, event: dict) -> dict:
        """Append a decision to the mission workbench."""
        return self.workbench_manager.append_decision(mission_id, event)

    def finalize_to_vault(self, mission_id: str, outcome: dict, learning_episode: dict | None = None) -> dict:
        """
        Finalize a mission workbench and curate valuable entries into the knowledge vault.
        Optionally accepts or creates a LearningEpisode and persists it to SessionStore.
        """
        # 1. Finalize Workbench
        meta = self.workbench_manager.finalize_workbench(mission_id, outcome)
        workbench_path = meta.get("workbench_ref")

        # 2. Extract and Store Vault Entries
        curation_report = self.vault_curator.finalize_and_clean(mission_id, workbench_path)
        vault_refs = [f".aiwg/vault/{vid}.json" for vid in curation_report.get("stored_ids", [])]
        
        # 3. Handle Learning Episode
        episode_data = learning_episode or {}
        episode_data.setdefault("episode_id", f"ep-{uuid.uuid4().hex[:8]}")
        episode_data.setdefault("mission_id", mission_id)
        
        # Ensure outcome is lowercased to match LearningEpisode OUTCOMES
        raw_outcome = outcome.get("status", "unknown").lower()
        if raw_outcome not in {"success", "partial", "failed", "blocked", "unknown"}:
            raw_outcome = "unknown"
            
        episode_data.setdefault("outcome", raw_outcome)
        episode_data.setdefault("session_id", "default")
        episode_data["workbench_ref"] = str(workbench_path)
        episode_data["vault_refs"] = vault_refs
        
        ep = LearningEpisode(**episode_data)
        ep_dict = ep.to_dict()
        
        learning_episode_ref = ""
        if self.session_store:
            learning_episode_ref = self.session_store.append_learning_episode(ep.session_id, ep_dict)

        # 4. Record in Phase Ledger
        if self.phase_ledger:
            self.phase_ledger.append_event(mission_id, {
                "event_type": "WORKBENCH_FINALIZED",
                "outcome_status": outcome.get("status", "unknown"),
                "vault_entries_created": curation_report.get("vault_entries_created", 0),
                "learning_episode_ref": learning_episode_ref,
            })
            
            for entry_id in curation_report.get("stored_ids", []):
                self.phase_ledger.append_event(mission_id, {
                    "event_type": "VAULT_ENTRY_STORED",
                    "vault_id": entry_id,
                    "vault_ref": f".aiwg/vault/{entry_id}.json",
                })

        return {
            "workbench_meta": meta,
            "curation_report": curation_report,
            "learning_episode": ep_dict,
            "learning_episode_ref": learning_episode_ref,
            "vault_refs": vault_refs,
        }
