import pytest
import os
import shutil
import sys

# Asegurar que las capas estén en el path para los tests
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l2_brain"))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l1_nervous"))

from adapters import KuzuRepository
from models import AuthorityLevel, IntentType

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
    h1 = "HASH_NODE_1"
    cypher1 = (
        f"CREATE (m:MemoryNode4D {{"
        f"causal_hash: '{h1}', "
        f"parent_hash: 'GENESIS', "
        f"lamport_t: 1, "
        f"locus_x: 'test', locus_y: 'unit', locus_z: 'recovery', "
        f"authority_a: 'ARCHITECT', "
        f"intent_i: 'MUTATION', "
        f"summary: 'Node 1', "
        f"timestamp: 123456789}})"
    )
    temp_kuzu.query(cypher1)
    
    # Nodo 2: Hijo de Nodo 1
    h2 = "HASH_NODE_2"
    cypher2 = (
        f"CREATE (m:MemoryNode4D {{"
        f"causal_hash: '{h2}', "
        f"parent_hash: '{h1}', "
        f"lamport_t: 2, "
        f"locus_x: 'test', locus_y: 'unit', locus_z: 'recovery', "
        f"authority_a: 'ARCHITECT', "
        f"intent_i: 'MUTATION', "
        f"summary: 'Node 2', "
        f"timestamp: 123456790}})"
    )
    temp_kuzu.query(cypher2)
    
    # 2. Recuperar cadena desde N2
    chain = temp_kuzu.get_causal_chain(h2)
    
    assert len(chain) == 2, "La cadena debe contener 2 nodos"
    assert chain[1].causal_hash == h1
    assert chain[0].causal_hash == h2
    assert chain[1].context.lamport_t < chain[0].context.lamport_t

def test_skill_provenance_link_mock(temp_kuzu):
    """Prueba la lógica de SkillRepository (simulada sobre KuzuRepository)."""
    # En el layout actual, el SkillRepository se integra con Kuzu
    # 1. Crear nodo de memoria fuente
    h1 = "ORIGIN_HASH"
    cypher = (
        f"CREATE (m:MemoryNode4D {{"
        f"causal_hash: '{h1}', "
        f"parent_hash: 'GENESIS', "
        f"lamport_t: 1, "
        f"locus_x: 'test', locus_y: 'unit', locus_z: 'skill', "
        f"authority_a: 'ARCHITECT', "
        f"intent_i: 'MUTATION', "
        f"summary: 'Origin Event', "
        f"timestamp: 123456789}})"
    )
    temp_kuzu.query(cypher)
    
    # 2. Verificar que el nodo existe
    node = temp_kuzu.get_by_hash(h1)
    assert node is not None
    assert node.causal_hash == h1
