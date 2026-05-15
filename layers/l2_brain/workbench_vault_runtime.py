from __future__ import annotations

import logging
from typing import Any

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
    ):
        self.workbench_manager = workbench_manager
        self.vault_curator = vault_curator
        self.phase_ledger = phase_ledger

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

    def finalize_to_vault(self, mission_id: str, outcome: dict) -> dict:
        """
        Finalize a mission workbench and curate valuable entries into the knowledge vault.
        """
        # 1. Finalize Workbench
        meta = self.workbench_manager.finalize_workbench(mission_id, outcome)
        workbench_path = meta.get("workbench_ref")

        # 2. Extract and Store Vault Entries
        curation_report = self.vault_curator.finalize_and_clean(mission_id, workbench_path)
        
        # 3. Record in Phase Ledger
        if self.phase_ledger:
            self.phase_ledger.append_event(mission_id, {
                "event_type": "WORKBENCH_FINALIZED",
                "outcome_status": outcome.get("status", "unknown"),
                "vault_entries_created": curation_report.get("vault_entries_created", 0),
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
        }
