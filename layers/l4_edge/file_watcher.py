import logging

logger = logging.getLogger("edge-observer")

class FileWatcher:
    """
    [L4_EDGE] Observador de cambios.
    Monitorea el sistema de archivos en busca de mutaciones externas.
    """
    def __init__(self, watch_path: str):
        self.path = watch_path
        self.enabled = False

    async def watch_forever(self):
        logger.warning(
            "L4 EDGE file watcher disabled until a real backend is implemented for %s",
            self.path,
        )
        return "DISABLED_PENDING_IMPLEMENTATION"
