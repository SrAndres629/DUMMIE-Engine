import pytest
from pathlib import Path
from layers.l2_brain.mission_workbench import MissionWorkbenchManager
from layers.l2_brain.vault_curator import VaultCurator
from layers.l2_brain.phase_ledger import PhaseLedger
from layers.l2_brain.workbench_vault_runtime import WorkbenchVaultRuntime

def test_workbench_vault_runtime_lifecycle(tmp_path):
    wb_root = tmp_path / "workbench"
    vault_root = tmp_path / "vault"
    ledger_root = tmp_path / "ledger"
    
    ledger = PhaseLedger(root=ledger_root)
    wb_manager = MissionWorkbenchManager(root=wb_root, phase_ledger=ledger)
    curator = VaultCurator(root=vault_root)
    
    runtime = WorkbenchVaultRuntime(wb_manager, curator, phase_ledger=ledger)
    
    mission_id = "mission_runtime_1"
    goal = "Test runtime coordination"
    
    # 1. Create
    runtime.create_for_mission(mission_id, goal)
    state = ledger.current_state(mission_id)
    assert state["workbench_ref"].endswith(f"{mission_id}/")
    
    # 2. Decision
    runtime.append_decision(mission_id, {"claim": "Use fcntl", "decision": "APPROVED"})
    
    # 3. Finalize
    wb_path = wb_root / mission_id
    (wb_path / "final_summary.md").write_text("# Golden path found here")
    
    res = runtime.finalize_to_vault(mission_id, {"status": "SUCCESS"})
    
    assert res["curation_report"]["vault_entries_created"] == 2 # decision + golden_path
    
    # 4. Check ledger
    final_state = ledger.current_state(mission_id)
    assert final_state["status"] == "finalized"
    assert len(final_state["vault_refs"]) == 2
    for vref in final_state["vault_refs"]:
        assert vref.startswith(".aiwg/vault/vlt-")
