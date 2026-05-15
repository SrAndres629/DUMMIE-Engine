import pytest
from pathlib import Path
from layers.l2_brain.mission_workbench import MissionWorkbenchManager
from layers.l2_brain.vault_curator import VaultCurator
from layers.l2_brain.token_cost_ledger import TokenCostLedger
from layers.l2_brain.context_budget_manager import ContextBudgetManager

def test_workbench_vault_integration_flow(tmp_path):
    wb_root = tmp_path / "workbench"
    vault_root = tmp_path / "vault"
    ledger_root = tmp_path / "ledger"
    
    budget_manager = ContextBudgetManager()
    wb_manager = MissionWorkbenchManager(root=wb_root, budget_manager=budget_manager)
    curator = VaultCurator(root=vault_root)
    
    mission_id = "mission_integration_1"
    
    # 1. Create workbench
    wb_manager.create_workbench(mission_id, "Integration Goal")
    wb_path = wb_root / mission_id
    
    # 2. Write some artifacts
    wb_manager.write_artifact(mission_id, "final_summary.md", "# Success pattern found", "summary")
    wb_manager.append_decision(mission_id, {"claim": "Use integration tests", "decision": "APPROVED"})
    
    # 3. Finalize
    wb_manager.finalize_workbench(mission_id, {"status": "SUCCESS"})
    
    # 4. Curate
    report = curator.finalize_and_clean(mission_id, wb_path)
    
    assert report["vault_entries_created"] == 2 # golden_path and decision
    
    # 5. Check vault
    index = curator.build_vault_index()
    assert index["total_entries"] == 2
    
    # 6. Verify workbench preserved
    assert wb_path.exists()
    assert (wb_path / "workbench_metadata.json").exists()
