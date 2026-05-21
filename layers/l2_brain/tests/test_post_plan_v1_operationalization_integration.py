import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.repo_intelligence_query import query_repo_intelligence
from layers.l2_brain.context.context_enforcement_gate import run_context_enforcement_gate
from layers.l2_brain.mission.dummie_chat_cli import DummieChatCli
from layers.l2_brain.governance.operationalization_review import run_operationalization_review

def test_operationalization_integration(tmp_path):
    aiwg = tmp_path / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    repo = tmp_path
    
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "evolution").mkdir(parents=True)
    
    (aiwg / "evolution" / "current_position.json").write_text(json.dumps({"current_phase": "P31"}))
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/module.py", "language": "python", "layer": "l2_brain", "is_runtime": True}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    (intel / "repo_intelligence_manifest.json").write_text(json.dumps({"repo_id": "test"}))

    # 1. Query
    q_res = query_repo_intelligence({"is_runtime": True}, aiwg_root=aiwg)
    assert q_res.count == 1
    
    # 2. Gate
    g_res = run_context_enforcement_gate({"task_type": "analysis"}, aiwg_root=aiwg)
    assert g_res.decision == "ALLOW_DOSSIER_CONTEXT"
    
    # 3. Chat
    chat = DummieChatCli(aiwg_root=aiwg)
    c_res = chat.handle_query("status")
    assert "phase P31" in c_res.answer
    
    # 4. Review
    # Mocking repairs for review
    (aiwg / "reports" / "spec_frontmatter_repair_latest.json").write_text(json.dumps({"decision": "PASS", "repaired_count": 1}))
    
    op_res = run_operationalization_review(aiwg_root=aiwg)
    assert op_res["decision"] == "PASS"
