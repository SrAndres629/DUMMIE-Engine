import os
import json
from typing import List
from brain.domain.memory.ports import IEventStorePort
from brain.domain.governance.models import LayerCertainty

class SemanticConsistencyAgent:
    """
    Agente de Consistencia Semántica (Spec 39).
    Valida que el código físico y las specs no diverjan.
    """
    def __init__(self, event_store: IEventStorePort):
        self.event_store = event_store

    def check_consistency(self, locus_x: str) -> dict:
        """
        Verifica si existe documentación indexada para un locus específico.
        """
        # Buscar en el 4D-TES nodos del locus 'doc.spec' vinculados
        doc_head = self.event_store.get_last_leaf_hash(locus_x="doc.spec")
        if doc_head == "GENESIS":
            return {
                "locus": locus_x,
                "status": "TERRA_INCOGNITA",
                "message": "No se encontró documentación indexada en el sistema."
            }
            
        doc_chain = self.event_store.get_causal_chain(doc_head)
        
        # Buscar si algún spec menciona este locus (simplificado: por nombre de archivo o metadata)
        matched_specs = []
        for node in doc_chain:
            metadata = json.loads(node.payload.decode())
            # Si el locus_y del spec contiene el locus_x que buscamos
            if locus_x in metadata.get("path", "") or locus_x in node.context.locus_y:
                matched_specs.append(metadata.get("path"))
        
        if not matched_specs:
            return {
                "locus": locus_x,
                "status": "DRIFT_DETECTED",
                "message": f"El locus {locus_x} no tiene una especificación vinculada."
            }
            
        return {
            "locus": locus_x,
            "status": "CONSISTENT",
            "linked_specs": matched_specs
        }
