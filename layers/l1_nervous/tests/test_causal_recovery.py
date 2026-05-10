import pytest
import os
import shutil
from brain.infrastructure.adapters.kuzu_repository import KuzuRepository, KuzuSkillRepository
from brain.domain.memory.models import MemoryNode4DTES, CrystallizedSkill
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType

@pytest.fixture
def temp_kuzu():
    # Usar una ruta temporal única para el test
    import uuid
    db_path = f".test_loci_{uuid.uuid4().hex}.db"
    if os.path.exists(db_path):
        # Limpieza profunda para Kuzu (borrar directorio)
        try:
            shutil.rmtree(db_path)
        except: pass
        
    repo = KuzuRepository(db_path=db_path)
    yield repo
    
    # Cleanup post-test
    try:
        shutil.rmtree(db_path)
    except: pass

def test_merkle_dag_causal_chain(temp_kuzu):
    """Prueba que el Merkle-DAG permite reconstruir la historia causal."""
    # 1. Crear cadena: GENESIS -> N1 -> N2
    ctx = SixDimensionalContext(
        locus_x="test", locus_y="unit", locus_z="merkle",
        lamport_t=1, authority_a=AuthorityLevel.ARCHITECT, intent_i=IntentType.MUTATION
    )
    
    n1 = MemoryNode4DTES.generate(parent_hash="GENESIS", context=ctx, payload=b"Node 1")
    temp_kuzu.append(n1)
    
    # Clonar contexto para incrementar tiempo
    ctx2 = ctx.model_copy()
    ctx2.lamport_t = 2
    
    n2 = MemoryNode4DTES.generate(parent_hash=n1.causal_hash, context=ctx2, payload=b"Node 2")
    temp_kuzu.append(n2)
    
    # 2. Recuperar cadena desde N2
    chain = temp_kuzu.get_causal_chain(n2.causal_hash)
    
    assert len(chain) == 2, "La cadena debe contener 2 nodos"
    assert chain[0].causal_hash == n1.causal_hash
    assert chain[1].causal_hash == n2.causal_hash
    assert chain[0].context.lamport_t < chain[1].context.lamport_t

def test_skill_provenance_link(temp_kuzu):
    """Prueba que las Skills se enlazan correctamente con su origen causal."""
    skill_repo = KuzuSkillRepository(temp_kuzu)
    
    # 1. Crear nodo de memoria fuente
    ctx = SixDimensionalContext(
        locus_x="test", locus_y="unit", locus_z="skill",
        lamport_t=1, authority_a=AuthorityLevel.ARCHITECT, intent_i=IntentType.MUTATION
    )
    n1 = MemoryNode4DTES.generate(parent_hash="GENESIS", context=ctx, payload=b"Origin Event")
    temp_kuzu.append(n1)
    
    # 2. Crear Skill cristalizada
    skill = CrystallizedSkill(
        skill_id="SKILL-PROVENANCE-TEST",
        yaml_payload="name: test_provenance\nrule: strict",
        source_causal_hashes=[n1.causal_hash],
        skill_hash="CRYPTOGRAPHIC_PROOF_001"
    )
    skill_repo.save_skill(skill)
    
    # 3. Recuperar Skill y verificar enlace al Merkle-DAG
    recovered = skill_repo.get_skill_by_id("SKILL-PROVENANCE-TEST")
    
    assert recovered is not None
    assert recovered.skill_id == "SKILL-PROVENANCE-TEST"
    assert n1.causal_hash in recovered.source_causal_hashes
    assert recovered.skill_hash == "CRYPTOGRAPHIC_PROOF_001"
