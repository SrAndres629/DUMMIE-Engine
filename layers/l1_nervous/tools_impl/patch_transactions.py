import json
from typing import Dict, Any, List

def create_patch_transaction(
    session_id: str,
    proposal_id: str,
    source_pattern_id: str,
    mission_id: str,
    affected_paths: List[str],
    diff_unified: str,
    tests_to_run: List[str],
    rollback_plan: str,
    safety_gates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    MCP Tool: dummie_patch_transaction_create
    Creates a patch transaction in dry-run mode. Returns the transaction status.
    """
    try:
        from layers.l2_brain.patch_transaction import PatchProposal
        from layers.l2_brain.patch_transaction_manager import PatchTransactionManager
        from layers.l2_brain.session_store import SessionStore
    except ImportError:
        return {"error": "L2 Brain modules not found. Cannot create transaction."}

    # In a real environment, we would inject the correct SessionStore instance here.
    # For now, we mock the dependency or load it from the known path.
    import os
    from pathlib import Path
    
    root_dir = os.getenv("DUMMIE_ROOT") or str(Path.cwd())
    store = SessionStore(root_dir)
    manager = PatchTransactionManager(store)
    
    proposal = PatchProposal(
        proposal_id=proposal_id,
        source_pattern_id=source_pattern_id,
        mission_id=mission_id,
        affected_paths=affected_paths,
        diff_unified=diff_unified,
        tests_to_run=tests_to_run,
        rollback_plan=rollback_plan,
        safety_gates=safety_gates
    )
    
    txn = manager.create_transaction(session_id, proposal)
    
    return {
        "status": "success",
        "transaction_id": txn.transaction_id,
        "transaction_status": txn.status,
        "evidence": txn.evidence_refs
    }


def get_patch_transaction_status(session_id: str, transaction_id: str) -> Dict[str, Any]:
    """
    MCP Tool: dummie_patch_transaction_status
    Retrieves the status of an existing patch transaction from the session artifacts.
    """
    try:
        from layers.l2_brain.session_store import SessionStore
    except ImportError:
        return {"error": "L2 Brain modules not found."}

    import os
    from pathlib import Path
    
    root_dir = os.getenv("DUMMIE_ROOT") or str(Path.cwd())
    store = SessionStore(root_dir)
    
    try:
        session = store.load_session(session_id)
        artifact_name = f"transaction_{transaction_id}.json"
        
        if artifact_name not in session["artifacts"]:
            return {"error": f"Transaction {transaction_id} not found in session {session_id}"}
            
        session_path = Path(session["path"])
        artifact_path = session_path / "artifacts" / artifact_name
        
        content = json.loads(artifact_path.read_text(encoding="utf-8"))
        return {"status": "success", "transaction": content}
        
    except Exception as e:
        return {"error": f"Failed to retrieve transaction: {str(e)}"}


def validate_patch_transaction(session_id: str, transaction_id: str) -> Dict[str, Any]:
    """
    MCP Tool: dummie_patch_transaction_validate
    Simulates validation of an awaiting transaction. Does not apply it.
    """
    # This would normally trigger the L2 Brain's validation runner.
    # For this phase, it just confirms it can read the transaction and returns a validation simulation.
    status_response = get_patch_transaction_status(session_id, transaction_id)
    if "error" in status_response:
        return status_response
        
    txn = status_response["transaction"]
    
    if txn["status"] != "AWAITING_APPROVAL":
        return {"error": f"Transaction cannot be validated in state: {txn['status']}"}
        
    return {
        "status": "success",
        "validation_state": "SIMULATED_PASS",
        "message": "Validation simulation complete. Transaction is safe but cannot be applied in Phase 5."
    }
