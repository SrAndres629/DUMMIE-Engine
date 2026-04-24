import os
import json
import fcntl
import logging
from datetime import datetime

logger = logging.getLogger("dummie-mcp.utils")

class AtomicLedgerWriter:
    """Escritor atómico para archivos JSONL en entornos concurrentes."""
    
    @staticmethod
    def append_entry(file_path: str, entry: dict):
        """Añade una entrada al archivo JSONL usando bloqueos de archivo (flock)."""
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Añadir timestamp si no existe
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
            
        line = json.dumps(entry) + "\n"
        
        try:
            with open(file_path, "a") as f:
                # Bloqueo exclusivo (bloqueante)
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(line)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    # Liberar bloqueo
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed atomic write to {file_path}: {str(e)}")
            raise
