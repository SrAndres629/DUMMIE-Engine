import logging
from typing import List

try:
    from .memory_ipc import ArrowMemoryBridge, MemoryPlaneError
except ImportError:
    try:
        # Compatibilidad cuando este módulo se importa como top-level desde mcp_server.py
        from memory_ipc import ArrowMemoryBridge, MemoryPlaneError
    except ImportError:
        # Fallback explícito para ejecuciones desde raíz de repo/scripts.
        from layers.l1_nervous.memory_ipc import ArrowMemoryBridge, MemoryPlaneError

logger = logging.getLogger("dummie-mcp.compressive-memory")

class CompressiveMemory:
    """
    Implementación del principio Infini-attention.
    Gestiona la compresión del historial y su persistencia en el 4D-TES (KùzuDB).
    """
    
    def __init__(self, bridge: ArrowMemoryBridge):
        self.bridge = bridge
        self.compression_threshold = 20000 # tokens
        self.summary_target_size = 2000 # tokens
        self.last_persist_ok = False
        self.last_error = ""
        self.last_causal_hash = ""

    def crystallize_history(self, history: List[str], require_persist: bool = False) -> str:
        """
        Toma una lista de mensajes y los comprime en un resumen persistente.
        Implementa extracción semántica estructurada (Production Hardening).
        """
        if not history:
            return "No hay historial para cristalizar."

        import re
        combined_text = "\n".join(history)
        logger.info(f"Crystallizing history: {len(combined_text)} chars")
        
        # Extracción semántica estructurada (Ontology Alignment)
        patterns = {
            "DECISIONES": [r"DECISION: (.*)", r"RESOLVED: (.*)", r"SELECTED: (.*)", r"APPROVED: (.*)"],
            "ERRORES": [r"ERROR: (.*)", r"FAIL: (.*)", r"CRITICAL: (.*)", r"EXCEPTION: (.*)"],
            "ESTADO_FABRICACION": [r"MOVED TO: (.*)", r"COMPONENT: (.*)", r"SPEC: (.*)"]
        }
        
        extracted = {k: [] for k in patterns}
        for msg in history:
            for category, regex_list in patterns.items():
                for regex in regex_list:
                    match = re.search(regex, msg, re.IGNORECASE)
                    if match:
                        extracted[category].append(match.group(1).strip())
        
        summary_blocks = [
            "--- CRISTALIZACIÓN DE MEMORIA INDUSTRIAL (V3.1) ---",
            f"T-CONTEXT: {len(history)} mensajes comprimidos.",
            "ARTEFACTOS DE DECISIÓN Y ESTADO:"
        ]
        
        for cat, items in extracted.items():
            if items:
                summary_blocks.append(f"  [{cat}]:")
                # Deduplicar y limitar
                unique_items = list(dict.fromkeys(items))
                for item in unique_items[:5]:
                    summary_blocks.append(f"    - {item[:150]}")
        
        summary_blocks.append(f"RESUMEN SEMÁNTICO: {combined_text[:350]}...")
        summary = "\n".join(summary_blocks)
        
        # Persistencia Determinista
        self.last_persist_ok = False
        self.last_error = ""
        self.last_causal_hash = ""

        try:
            if not self.bridge.heartbeat():
                msg = "Memory Plane not available for crystallization."
                logger.warning(msg)
                if require_persist:
                    self.last_error = msg
                    raise MemoryPlaneError("ERR_CONNECTION_REFUSED", msg)
                # En modo offline permitido no intentamos escribir: evitamos ruido y errores colaterales.
                return summary
            
            import time
            try:
                from models import MemoryNode4D
            except ImportError:
                from layers.l2_brain.models import MemoryNode4D
            
            # [HARDENING] Saneamiento de Cadena Causal
            # No usamos strings arbitrarios como 'COMPRESSED_CONTEXT'.
            # Buscamos el último hash para mantener el Merkle-DAG íntegro.
            try:
                # Intentamos obtener el último hash de la DB si es posible a través del bridge/repo
                try:
                    from layers.l2_brain.adapters import KuzuRepository
                except ImportError:
                    from adapters import KuzuRepository
                
                repo = KuzuRepository(db=self.bridge)
                parent_hash = repo.get_last_leaf_hash()
                logger.info(f"Causal link identified: parent={parent_hash}")
            except Exception as e:
                logger.warning(f"Causal link fallback to GENESIS: {e}")
                parent_hash = "GENESIS"

            causal_hash, cypher = MemoryNode4D.build_create_cypher(
                parent_hash=parent_hash,
                locus_x='layers.l1_nervous.compression',
                locus_y='L1_TRANSPORT',
                locus_z='L2_BRAIN',
                lamport_t=int(time.time()),
                authority_a='OVERSEER',
                intent_i='CRYSTALLIZATION',
                payload=summary,
                content_to_hash=combined_text
            )
            self.last_causal_hash = causal_hash
            
            self.bridge.ipc.execute(cypher)
            logger.info(f"Crystallization persisted (SOVEREIGN-4D): {causal_hash}")
            self.last_persist_ok = True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Persistence failure: {e}")
            if require_persist:
                raise
            
        return summary

    def get_compressed_context(self, current_history: List[str]) -> List[str]:
        """
        Retorna el contexto optimizado: [Último Resumen] + [Mensajes Recientes].
        """
        if len("\n".join(current_history)) < self.compression_threshold:
            return current_history
            
        # Disparar compresión
        summary = self.crystallize_history(current_history[:-5]) # Mantener los últimos 5 mensajes
        return [summary] + current_history[-5:]

def initialize_compressive_memory(socket_path: str = "/tmp/dummie_memory.sock") -> CompressiveMemory:
    bridge = ArrowMemoryBridge(socket_path)
    return CompressiveMemory(bridge)
