import json
from typing import List
from brain.domain.memory.ports import IEventStorePort
from brain.domain.memory.models import MemoryNode4DTES

class MetacognitiveAuditor:
    """
    Auditor Metacognitivo (Spec 40).
    Verifica la integridad estructural del Palacio de Loci.
    """
    def __init__(self, event_store: IEventStorePort):
        self.event_store = event_store

    def run_audit(self) -> dict:
        """Realiza un chequeo de salud del sistema."""
        issues = []
        
        # 1. Verificar el head actual
        head_hash = self.event_store.get_last_leaf_hash()
        if head_hash == "GENESIS":
            return {"status": "HEALTHY", "nodes": 0, "issues": []}
            
        # 2. Reconstruir cadena y verificar punteros
        chain = self.event_store.get_causal_chain(head_hash)
        
        # Verificar integridad Merkle (simplificado)
        for i in range(1, len(chain)):
            current = chain[i]
            parent = chain[i-1]
            if current.parent_hash != parent.causal_hash:
                issues.append({
                    "type": "CAUSAL_BREAK",
                    "node": current.causal_hash,
                    "expected_parent": parent.causal_hash,
                    "actual_parent": current.parent_hash
                })
        
        # 3. Detectar nodos tóxicos (Spec 10/40)
        # Por ahora simulamos que no hay toxicidad
        
        return {
            "status": "HEALTHY" if not issues else "DEGRADED",
            "node_count": len(chain),
            "issues": issues,
            "integrity_score": max(0, 1.0 - (len(issues) / len(chain))) if chain else 1.0
        }
