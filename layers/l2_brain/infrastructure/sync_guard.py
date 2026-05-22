import logging
import asyncio
from typing import Callable, Any, Coroutine

logger = logging.getLogger("brain.sync_guard")

class AtomicSyncGuard:
    """
    [L2_BRAIN] Guardián de Atomicidad.
    Garantiza la consistencia entre Git (Source of Truth) y Kuzu (Indexing).
    """
    def __init__(self, git_port, kuzu_port):
        self.git = git_port
        self.kuzu = kuzu_port

    async def run(self, git_op: Callable[[], Coroutine[Any, Any, None]], kuzu_op: Callable[[], Coroutine[Any, Any, None]]):
        # 1. Snapshot del estado previo
        pre_hash = await self.git.get_current_head()
        logger.info(f"SyncGuard: Iniciando transacción. HEAD={pre_hash}")

        try:
            # 2. Ejecutar operación Git
            await git_op()
            
            # 3. Ejecutar operación Kuzu
            await kuzu_op()
            
        except Exception as e:
            logger.error(f"SyncGuard: Fallo detectado. Ejecutando rollback a {pre_hash}. Error: {e}")
            await self.git.rollback(pre_hash)
            raise e
        
        logger.info("SyncGuard: Transacción completada con éxito.")
