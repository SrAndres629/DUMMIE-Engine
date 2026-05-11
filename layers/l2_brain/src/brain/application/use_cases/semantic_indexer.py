import os
import hashlib
import json
from datetime import datetime
from typing import List
from brain.domain.memory.ports import IEventStorePort
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
from brain.domain.memory.models import MemoryNode4DTES

class SemanticFabricIndexer:
    """
    Indexador de la "Tela Semántica" (Spec 41).
    Vincula la documentación física (Markdown) con el grafo de memoria.
    """
    def __init__(self, event_store: IEventStorePort):
        self.event_store = event_store

    def index_docs(self, docs_path: str) -> int:
        """Escanea recursivamente y añade nodos de memoria para cada spec."""
        indexed_count = 0
        if not os.path.exists(docs_path):
            return 0
            
        for root, _, files in os.walk(docs_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Crear contexto para la documentación
                        rel_path = os.path.relpath(file_path, docs_path)
                        context = SixDimensionalContext(
                            locus_x="doc.spec",
                            locus_y=rel_path.replace("/", "."),
                            locus_z="v1",
                            lamport_t=0, # Base temporal
                            authority_a=AuthorityLevel.ARCHITECT,
                            intent_i=IntentType.OBSERVATION
                        )
                        
                        # Payload con metadata del spec
                        payload = {
                            "filename": file,
                            "path": rel_path,
                            "hash": hashlib.sha256(content.encode()).hexdigest(),
                            "indexed_at": datetime.utcnow().isoformat()
                        }
                        
                        # Encadenar en el 4D-TES
                        parent_hash = self.event_store.get_last_leaf_hash(locus_x="doc.spec")
                        node = MemoryNode4DTES.create(
                            parent_hash=parent_hash,
                            context=context,
                            payload=json.dumps(payload).encode()
                        )
                        
                        self.event_store.append_node(node)
                        indexed_count += 1
                    except Exception as e:
                        print(f"[SemanticIndexer] Error indexando {file}: {e}")
                        
        return indexed_count
