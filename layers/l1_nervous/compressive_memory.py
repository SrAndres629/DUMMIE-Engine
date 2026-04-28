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
            
            import hashlib
            import time
            causal_hash = hashlib.sha256(combined_text.encode()).hexdigest()[:24]
            self.last_causal_hash = causal_hash
            
            now_ms = int(time.time() * 1000)
            safe_summary = summary.replace("'", "''")
            
            # Unificación con el esquema MemoryNode4D de L2_BRAIN
            cypher = (
                f"CREATE (m:MemoryNode4D {{"
                f"causal_hash: '{causal_hash}', "
                f"parent_hash: 'COMPRESSED_CONTEXT', "
                f"lamport_t: {now_ms}, " # Fallback si no hay acceso al reloj global
                f"locus_x: 'layers.l1_nervous.compression', "
                f"locus_y: 'L1_TRANSPORT', "
                f"locus_z: 'L2_BRAIN', "
                f"authority_a: 'OVERSEER', "
                f"intent_i: 'CONTEXT', "
                f"summary: '{safe_summary}', "
                f"timestamp: {now_ms}}})"
            )
            
            self.bridge.ipc.execute(cypher)
            logger.info(f"Crystallization persisted (MemoryNode4D): {causal_hash}")
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
