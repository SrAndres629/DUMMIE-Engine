import pytest
import os
import shutil
import asyncio
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter

@pytest.fixture
def clean_env(tmp_path):
    # Usar rutas temporales únicas
    db_path = str(tmp_path / "test_chain.db")
    ledger_path = str(tmp_path / "test_decisions.jsonl")
    lessons_path = str(tmp_path / "test_lessons.jsonl")
    ambiguities_path = str(tmp_path / "test_ambiguities.jsonl")
    map_path = str(tmp_path / "test_ontological_map.json")
    
    kuzu_repo = KuzuRepository(db_path=db_path)
    skill_repo = KuzuSkillRepository(db_path=db_path)
    ledger = DecisionLedgerAdapter(
        ledger_path=ledger_path,
        lessons_path=lessons_path,
        ambiguities_path=ambiguities_path,
        ontological_map_path=map_path
    )
    shield = NativeShieldAdapter()
    
    session_path = str(tmp_path / "test_session.jsonl")
    session = SessionLedgerAdapter(ledger_path=session_path)
    
    orchestrator = CognitiveOrchestrator(
        shield_port=shield,
        event_store=kuzu_repo,
        ledger_audit=ledger,
        skill_repo=skill_repo,
        session_ledger=session
    )
    
    return orchestrator, kuzu_repo

@pytest.mark.anyio
async def test_3_sequential_tasks_chaining(clean_env):
    """
    PRUEBA DE FUEGO: Verifica que el Orquestador mantiene el encadenamiento causal 
    y el tiempo lógico de Lamport a través de múltiples tareas.
    """
    orchestrator, kuzu = clean_env
    
    # Tarea 1: El origen
    res1 = await orchestrator.handle_task("Tarea Alpha: Inicialización")
    assert res1 == "INTENT_QUEUED_L2_VALIDATED"
    
    head1 = kuzu.get_last_leaf_hash()
    node1 = kuzu.get_by_hash(head1)
    assert node1.parent_hash == "GENESIS", "La primera tarea debe ser raíz"
    assert node1.context.lamport_t == 1, "Tick inicial debe ser 1"
    
    # Tarea 2: El primer eslabón
    res2 = await orchestrator.handle_task("Tarea Beta: Mutación de LST")
    assert res2 == "INTENT_QUEUED_L2_VALIDATED"
    
    head2 = kuzu.get_last_leaf_hash()
    node2 = kuzu.get_by_hash(head2)
    assert node2.parent_hash == head1, "La segunda tarea debe apuntar a la primera"
    assert node2.context.lamport_t == 2, "El tiempo de Lamport debe incrementarse"
    
    # Tarea 3: El cierre de la cadena
    res3 = await orchestrator.handle_task("Tarea Gamma: Auditoría Final")
    assert res3 == "INTENT_QUEUED_L2_VALIDATED"
    
    head3 = kuzu.get_last_leaf_hash()
    node3 = kuzu.get_by_hash(head3)
    assert node3.parent_hash == head2, "La tercera tarea debe apuntar a la segunda"
    assert node3.context.lamport_t == 3, "El tiempo de Lamport debe incrementarse a 3"
    
    # Verificar integridad del Merkle-DAG recuperando la cadena completa
    chain = kuzu.get_causal_chain(head3)
    assert len(chain) == 3
    assert chain[2].causal_hash == head1
    assert chain[1].causal_hash == head2
    assert chain[0].causal_hash == head3
    
    print(f"\n[SUCCESS] Cadena Causal Verificada: GENESIS -> {head1[:8]} -> {head2[:8]} -> {head3[:8]}")
