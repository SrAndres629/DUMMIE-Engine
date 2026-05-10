import pytest
import os
import json
import shutil
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.domain.context.models import AuthorityLevel

@pytest.fixture
def clean_env(tmp_path):
    db_path = str(tmp_path / "test_loci.db")
    ledger_path = str(tmp_path / "test_resolutions.jsonl")
    session_path = str(tmp_path / "test_session.jsonl")
    ont_map_path = str(tmp_path / "test_ontological_map.json")
    
    repo = KuzuRepository(db_path)
    ledger = DecisionLedgerAdapter(
        ledger_path=ledger_path,
        lessons_path=str(tmp_path / "test_lessons.jsonl"),
        ambiguities_path=str(tmp_path / "test_ambiguities.jsonl"),
        ontological_map_path=ont_map_path
    )
    session = SessionLedgerAdapter(session_path)
    shield = NativeShieldAdapter()
    skill_repo = KuzuSkillRepository(db_path=db_path)
    
    orchestrator = CognitiveOrchestrator(
        event_store=repo,
        ledger_audit=ledger,
        session_ledger=session,
        shield_port=shield,
        skill_repo=skill_repo
    )
    
    return {
        "orchestrator": orchestrator,
        "repo": repo,
        "ledger": ledger,
        "session": session,
        "paths": {
            "db": db_path,
            "ledger": ledger_path,
            "session": session_path,
            "map": ont_map_path
        }
    }

@pytest.mark.anyio
async def test_full_governance_cycle(clean_env):
    orchestrator = clean_env["orchestrator"]
    session = clean_env["session"]
    ledger = clean_env["ledger"]
    
    # 1. Verify Initial Certainty (Spec 42)
    cert = ledger.get_certainty_for_locus("sw.plant.orchestrator")
    assert cert.certainty_score == 0.0 # Initial state
    
    # 2. Process a task
    result = await orchestrator.handle_task("Industrializing L2_Brain Phase 1")
    assert result == "INTENT_QUEUED_L2_VALIDATED"
    
    # 3. Verify Session Ledger (Spec 36)
    history = session.get_session_history("default")
    assert len(history) == 1
    assert history[0].action == "TASK_HANDLED"
    assert "Phase 1" in history[0].thought_vector
    
    # 4. Verify Decision Ledger (Spec 34)
    with open(clean_env["paths"]["ledger"], "r") as f:
        line = f.readline()
        data = json.loads(line)
        assert data["tick"] == 1
        assert "impact" in data # Mapped from impact_blast_radius
        
    # 5. Verify Certainty Jump (Spec 42)
    cert = ledger.get_certainty_for_locus("sw.plant.orchestrator")
    assert cert.certainty_score == 1.0 # 1 test / 1 total
    assert os.path.exists(clean_env["paths"]["map"])
    
    # 6. Verify Threshold Lock (Spec 42)
    from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
    from brain.domain.context.models import IntentType as ContextIntent
    intent = AgentIntent(
        locus_x="sw.plant.coder",
        intent_i=ContextIntent.MUTATION,
        intent_type=FabricationIntent.WRITE_FILE,
        target="file.py",
        risk_score=0.9,
        rationale="Breaking things with low certainty",
        authority_a=AuthorityLevel.AGENT
    )
    # This should fail due to certainty 0.0 < 0.5
    with pytest.raises(Exception) as exc:
        await orchestrator.handle_task(intent)
    assert "Ontological lock" in str(exc.value)

@pytest.mark.anyio
async def test_structural_impact_analysis(clean_env):
    orchestrator = clean_env["orchestrator"]
    repo = clean_env["repo"]

    # Create a chain of nodes
    await orchestrator.handle_task("Node 1")
    await orchestrator.handle_task("Node 2")
    await orchestrator.handle_task("Node 3")

    head = repo.get_last_leaf_hash()
    chain = repo.get_causal_chain(head)
    assert len(chain) == 3

    # Analyze impact of the FIRST node (last in chain list which is leaf->root)
    root_hash = chain[2].causal_hash
    impact = repo.compute_blast_radius(root_hash)

    # The children of Node 1 are Node 2 and Node 3
    assert impact["total_impacted_nodes"] >= 1
    assert impact["impact_level"] == "LOW"
