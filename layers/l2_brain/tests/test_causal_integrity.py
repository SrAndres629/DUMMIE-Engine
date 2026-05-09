import pytest
try:
    from layers.l2_brain.models import MemoryNode4D, AuthorityLevel, IntentType
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models import MemoryNode4D, AuthorityLevel, IntentType

def test_causal_hash_sensitivity():
    """Verifica que el hash cambie si cambia cualquier dimensión del contexto o el payload."""
    base_args = {
        "parent_hashes": ["GENESIS"],
        "locus_x": "x",
        "locus_y": "y",
        "locus_z": "z",
        "lamport_t": 1,
        "authority_a": AuthorityLevel.AGENT,
        "intent_i": IntentType.FABRICATION,
        "payload": "content"
    }
    
    node_base = MemoryNode4D.from_intent_context(**base_args)
    h_base = node_base.causal_hash
    
    # 1. Cambio en Payload
    args_payload = base_args.copy()
    args_payload["payload"] = "different content"
    h_payload = MemoryNode4D.from_intent_context(**args_payload).causal_hash
    assert h_base != h_payload, "Hash should change with payload"
    
    # 2. Cambio en Autoridad
    args_auth = base_args.copy()
    args_auth["authority_a"] = AuthorityLevel.HUMAN
    h_auth = MemoryNode4D.from_intent_context(**args_auth).causal_hash
    assert h_base != h_auth, "Hash should change with authority"
    
    # 3. Cambio en Tiempo (Lamport)
    args_time = base_args.copy()
    args_time["lamport_t"] = 2
    h_time = MemoryNode4D.from_intent_context(**args_time).causal_hash
    assert h_base != h_time, "Hash should change with lamport_t"
    
    # 4. Cambio en Intención
    args_intent = base_args.copy()
    args_intent["intent_i"] = IntentType.AUDIT
    h_intent = MemoryNode4D.from_intent_context(**args_intent).causal_hash
    assert h_base != h_intent, "Hash should change with intent_i"

def test_causal_hash_no_truncation():
    """Verifica que el hash sea el SHA-256 completo (64 chars)."""
    node = MemoryNode4D.from_intent_context(
        ["GENESIS"], "x", "y", "z", 1, AuthorityLevel.AGENT, IntentType.FABRICATION, "content"
    )
    assert len(node.causal_hash) == 64, "Causal hash must be a full SHA-256 hex string (64 chars)"

def test_tamper_detection(tmp_path):
    """Verifica que si un nodo es alterado en la DB, get_by_hash levante ValueError."""
    from layers.l2_brain.adapters import KuzuRepository
    from layers.l2_brain.models import MemoryNode4D, AuthorityLevel, IntentType
    
    db_file = str(tmp_path / "test_db")
    repo = KuzuRepository(db_path=db_file)
    
    # 1. Crear nodo válido
    node = MemoryNode4D.from_intent_context(
        parent_hashes=["GENESIS"],
        locus_x="x", locus_y="y", locus_z="z",
        lamport_t=1,
        authority_a=AuthorityLevel.AGENT,
        intent_i=IntentType.FABRICATION,
        payload="valid_content"
    )
    
    repo.create_memory_node(node)
    
    # 2. Verificar que se puede leer
    read_node = repo.get_by_hash(node.causal_hash)
    assert read_node is not None
    
    # 3. Simulamos corrupción modificando el comportamiento de query
    class TamperedRepo(KuzuRepository):
        def query(self, cypher, parameters=None):
            class MockRes:
                def has_next(self): return True
                def get_next(self):
                    return [
                        node.causal_hash,
                        node.parent_hashes,
                        node.locus_x, node.locus_y, node.locus_z,
                        node.lamport_t,
                        node.authority_a,
                        node.intent_i,
                        "TAMPERED_CONTENT", # Alterado!
                        node.payload_hash,
                        node.embedding
                    ]
            return MockRes()
            
    tampered_repo = TamperedRepo(db=repo.db)
    tampered_repo.conn = repo.conn
    
    import pytest
    with pytest.raises(ValueError, match="Causal Integrity Failure"):
        tampered_repo.get_by_hash(node.causal_hash)
