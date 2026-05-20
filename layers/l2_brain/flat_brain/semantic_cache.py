import hashlib
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("brain.cache")

class SemanticCache:
    """
    [L2_BRAIN] Capa de ahorro de tokens.
    Evita repetir llamadas al modelo si la query o el contexto son idénticos.
    """
    def __init__(self, kuzu_repo: Any):
        self.kuzu_repo = kuzu_repo
        self._local_memory: Dict[str, str] = {} # Hash -> Response

    def _generate_hash(self, prompt: str, system_prompt: str) -> str:
        content = f"S:{system_prompt}|P:{prompt}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def get(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        h = self._generate_hash(prompt, system_prompt)
        
        # 1. Check local memory (fastest)
        if h in self._local_memory:
            logger.info(f"Cache HIT (Local): {h[:8]}")
            return self._local_memory[h]
        
        # 2. Check 4D-TES (Persistent)
        # En el futuro usaríamos búsqueda semántica real aquí.
        # Por ahora buscamos por ID exacto en el grafo.
        try:
            # Simulamos búsqueda en Kuzu por ahora
            # MATCH (n:MemoryNode4D {hash: $h}) RETURN n.payload
            pass
        except Exception as e:
            logger.debug(f"Cache miss or error in 4D-TES: {e}")
            
        return None

    async def set(self, prompt: str, response: str, system_prompt: str = ""):
        h = self._generate_hash(prompt, system_prompt)
        self._local_memory[h] = response
        
        # Persistir en 4D-TES para que sobreviva reinicios
        try:
            if self.kuzu_repo:
                from models import MemoryNode4D
                mem_node = MemoryNode4D.from_intent_context(
                    payload=response,
                    locus_x="cache",
                    locus_y="L2_BRAIN",
                    locus_z="PERSISTENCE",
                    authority_a="SEMANTIC_CACHE",
                    intent_i="CACHED_RESPONSE",
                    prompt_hash=h
                )
                self.kuzu_repo.create_memory_node(mem_node)
        except Exception as e:
            logger.warning(f"Failed to persist cache entry in 4D-TES: {e}")
