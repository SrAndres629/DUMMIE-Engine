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
        "parent_hash": "GENESIS",
        "locus_x": "x",
        "locus_y": "y",
        "locus_z": "z",
        "lamport_t": 1,
        "authority_a": AuthorityLevel.AGENT,
        "intent_i": IntentType.FABRICATION,
        "payload": "content"
    }
    
    h_base, _ = MemoryNode4D.build_create_cypher(**base_args)
    
    # 1. Cambio en Payload
    args_payload = base_args.copy()
    args_payload["payload"] = "different content"
    h_payload, _ = MemoryNode4D.build_create_cypher(**args_payload)
    assert h_base != h_payload, "Hash should change with payload"
    
    # 2. Cambio en Autoridad
    args_auth = base_args.copy()
    args_auth["authority_a"] = AuthorityLevel.HUMAN
    h_auth, _ = MemoryNode4D.build_create_cypher(**args_auth)
    assert h_base != h_auth, "Hash should change with authority"
    
    # 3. Cambio en Tiempo (Lamport)
    args_time = base_args.copy()
    args_time["lamport_t"] = 2
    h_time, _ = MemoryNode4D.build_create_cypher(**args_time)
    assert h_base != h_time, "Hash should change with lamport_t"
    
    # 4. Cambio en Intención
    args_intent = base_args.copy()
    args_intent["intent_i"] = IntentType.AUDIT
    h_intent, _ = MemoryNode4D.build_create_cypher(**args_intent)
    assert h_base != h_intent, "Hash should change with intent_i"

def test_causal_hash_no_truncation():
    """Verifica que el hash sea el SHA-256 completo (64 chars)."""
    h, _ = MemoryNode4D.build_create_cypher(
        "GENESIS", "x", "y", "z", 1, AuthorityLevel.AGENT, IntentType.FABRICATION, "content"
    )
    assert len(h) == 64, "Causal hash must be a full SHA-256 hex string (64 chars)"
