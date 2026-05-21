# Spec Reference: 05_orchestration_stack_and_glue
import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("dummie.l2.event_bus")


class AsyncEventBus:
    """
    [L2_BRAIN] Bus de eventos asíncrono intra-proceso.
    Permite la comunicación desacoplada entre los componentes del Daemon (Sagas, Auditores, etc).
    Reemplaza la dependencia en NATS externo para la fase de Gateway.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Any]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._worker_task = None

    def subscribe(self, event_type: str, callback: Callable[[Any], Any]):
        """Registra un callback para un tipo de evento específico."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Suscrito {callback.__name__} a evento '{event_type}'")

    async def publish(self, event_type: str, payload: Any):
        """Publica un evento en el bus."""
        await self._queue.put({"type": event_type, "payload": payload})
        logger.debug(f"Publicado evento '{event_type}'")

    async def start(self):
        """Inicia el worker que procesa los eventos."""
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._process_events())
        logger.info("AsyncEventBus worker iniciado.")

    async def stop(self):
        """Detiene el worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("AsyncEventBus worker detenido.")

    async def _process_events(self):
        while self._running:
            try:
                event = await self._queue.get()
                event_type = event["type"]
                payload = event["payload"]

                if event_type in self._subscribers:
                    for callback in self._subscribers[event_type]:
                        try:
                            # Soporta callbacks síncronos y asíncronos
                            if asyncio.iscoroutinefunction(callback):
                                await callback(payload)
                            else:
                                callback(payload)
                        except Exception as e:
                            logger.error(
                                f"Error procesando evento '{event_type}' en {callback.__name__}: {e}"
                            )
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error fatal en el worker del EventBus: {e}")
