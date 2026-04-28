import pytest
import os
import shutil
import sys

# Asegurar que las capas estén en el path para los tests
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l2_brain"))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l1_nervous"))

from adapters import KuzuRepository
from models import AuthorityLevel, IntentType, MemoryNode4D

@pytest.fixture
def temp_kuzu(tmp_path):
    db_path = str(tmp_path / "test_recovery.db")
    if os.path.exists(db_path):
        if os.path.isdir(db_path):
            shutil.rmtree(db_path)
        else:
            os.remove(db_path)
            
    repo = KuzuRepository(db_path=db_path)
    return repo

def test_merkle_dag_causal_chain_direct(temp_kuzu):
    """Prueba que el Merkle-DAG permite reconstruir la historia causal inyectando nodos directamente."""
    # Simular inserción de nodos (lo que haría el orchestrator)
    # Nodo 1: GENESIS
    h1, cypher1 = MemoryNode4D.build_create_cypher(
        parent_hash='GENESIS',
        locus_x='test',
        locus_y='unit',
        locus_z='recovery',
        lamport_t=1,
        authority_a='OVERSEER',
        intent_i='RESOLUTION',
        payload='Node 1 content'
    )
    temp_kuzu.query(cypher1)
    
    # Nodo 2: Hijo de Nodo 1
    h2, cypher2 = MemoryNode4D.build_create_cypher(
        parent_hash=h1,
        locus_x='test',
        locus_y='unit',
        locus_z='recovery',
        lamport_t=2,
        authority_a='OVERSEER',
        intent_i='RESOLUTION',
        payload='Node 2 content'
    )
    temp_kuzu.query(cypher2)
    
    # 2. Recuperar cadena desde N2
    chain = temp_kuzu.get_causal_chain(h2)
    
    assert len(chain) == 2, "La cadena debe contener 2 nodos"
    assert chain[1].causal_hash == h1
    assert chain[0].causal_hash == h2
    assert chain[1].context.lamport_t == 1
    assert chain[0].context.lamport_t == 2
    assert chain[0].payload == 'Node 2 content'

def test_skill_provenance_link_mock(temp_kuzu):
    """Prueba la lógica de recuperación por hash con el esquema SOVEREIGN-4D."""
    # 1. Crear nodo de memoria fuente
    h1, cypher = MemoryNode4D.build_create_cypher(
        parent_hash='GENESIS',
        locus_x='test',
        locus_y='unit',
        locus_z='skill',
        lamport_t=1,
        authority_a='OVERSEER',
        intent_i='CRYSTALLIZATION',
        payload='Origin Event'
    )
    temp_kuzu.query(cypher)
    
    # 2. Verificar que el nodo existe y tiene los campos correctos
    node = temp_kuzu.get_by_hash(h1)
    assert node is not None
    assert node.causal_hash == h1
    assert node.payload == "Origin Event"
    # El payload hash es generado por build_create_cypher
    import hashlib
    expected_hash = f"sha256:{hashlib.sha256(b'Origin Event').hexdigest()}"
    assert node.payload_hash == expected_hash
