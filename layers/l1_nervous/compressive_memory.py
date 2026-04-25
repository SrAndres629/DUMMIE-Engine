import logging
from typing import List

try:
    from .memory_ipc import ArrowMemoryBridge, MemoryPlaneError
except ImportError:
    # Compatibilidad cuando este módulo se importa como top-level desde mcp_server.py
    from memory_ipc import ArrowMemoryBridge, MemoryPlaneError

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
        Se categoriza la información para mantener coherencia ontológica.
        """
        if not history:
            return "No hay historial para cristalizar."

        combined_text = "\n".join(history)
        logger.info(f"Crystallizing history: {len(combined_text)} chars")
        
        # Simulación de extracción ontológica (En el futuro esto lo hace Gemini 1.5 Flash)
        # Extraemos intenciones y decisiones clave
        decisions = [line for line in history if "RESOLVED" in line or "DECISION" in line]
        errors = [line for line in history if "ERROR" in line or "FAIL" in line]
        
        summary_blocks = [
            "--- CRISTALIZACIÓN DE MEMORIA (4D-TES) ---",
            f"T-CONTEXT: {len(history)} mensajes comprimidos.",
            "DECISIONES CLAVE:",
            "\n".join(f"  - {d[:150]}" for d in decisions[:3]) if decisions else "  - Ninguna detectada.",
            "ERRORES/APRENDIZAJES:",
            "\n".join(f"  - {e[:150]}" for e in errors[:3]) if errors else "  - Sin fallos críticos.",
            f"RESUMEN SEMÁNTICO: {combined_text[:300]}..."
        ]
        summary = "\n".join(summary_blocks)
        
        # Persistir en KùzuDB vía IPC
        self.last_persist_ok = False
        self.last_error = ""
        self.last_causal_hash = ""

        try:
            # Asegurarse de que el bridge esté conectado
            if not self.bridge.heartbeat():
                msg = "Memory Plane not available for crystallization."
                logger.warning(msg)
                if require_persist:
                    self.last_error = msg
                    raise MemoryPlaneError("ERR_CONNECTION_REFUSED", msg)
            
            # Crear nodo de memoria con hash causal (simplificado)
            import hashlib
            causal_hash = hashlib.sha256(combined_text.encode()).hexdigest()[:16]
            self.last_causal_hash = causal_hash
            
            # Escapar comillas para Cypher
            safe_summary = summary.replace("'", "''")
            cypher = f"CREATE (m:MemoryState {{id: '{causal_hash}', summary: '{safe_summary}', type: 'crystallized', timestamp: timestamp()}})"
            
            self.bridge.ipc.execute(cypher)
            logger.info(f"Crystallization successful: {causal_hash}")
            self.last_persist_ok = True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error persisting crystallization: {e}")
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
