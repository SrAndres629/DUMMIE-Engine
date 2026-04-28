import pytest
import os
import time

try:
    from layers.l2_brain.adapters import KuzuRepository
    from layers.l1_nervous.compressive_memory import CompressiveMemory
    from layers.l2_brain.models import MemoryNode4D, AuthorityLevel, IntentType
except ImportError:
    import sys
    import os
    # Asegurar que los directorios de las capas estén en el path
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sys.path.insert(0, os.path.join(root, "l2_brain"))
    sys.path.insert(0, os.path.join(root, "l1_nervous"))
    from adapters import KuzuRepository
    from compressive_memory import CompressiveMemory
    from models import MemoryNode4D, AuthorityLevel, IntentType

class MockBridge:
    def __init__(self, conn):
        self.ipc = conn
    def heartbeat(self):
        return True

def test_compressive_memory_causal_link(tmp_path):
    """Verifica que los nodos comprimidos se enlacen correctamente al head de la DB."""
    db_path = str(tmp_path / "chain_db")
    # Inicializar repo real para el test
    repo = KuzuRepository(db_path=db_path)
    
    # 1. Crear un nodo inicial (Génesis -> N1)
    h1, c1 = MemoryNode4D.build_create_cypher(
        "GENESIS", "x", "y", "z", 100, AuthorityLevel.AGENT, IntentType.FABRICATION, "First"
    )
    repo.query(c1)
    
    # 2. Ejecutar compresión (debe apuntar a h1)
    # Importante: CompressiveMemory usa el bridge.ipc para ejecutar queries.
    # Pero para buscar el parent_hash, el hardening que añadí hace:
    # repo = KuzuRepository(db=self.bridge) -> espera bridge.ipc
    bridge = MockBridge(repo.conn)
    cm = CompressiveMemory(bridge)
    
    # Simular cristalización
    summary = cm.crystallize_history(["msg1", "msg2"], require_persist=True)
    
    # 3. Verificar en la DB que el nuevo nodo tiene parent == h1
    h_comp = cm.last_causal_hash
    node_comp = repo.get_by_hash(h_comp)
    
    assert node_comp is not None
    assert node_comp.parent_hash == h1, f"Compressed node should point to {h1}, got {node_comp.parent_hash}"
    assert node_comp.intent_i == IntentType.CRYSTALLIZATION
