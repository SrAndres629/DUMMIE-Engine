import asyncio
import logging
from typing import Callable, Dict, Any, List, Tuple, Optional

logger = logging.getLogger("nervous.broker")

class EventBroker:
    """
    Broker de Eventos y Comandos Interno (CQRS/Event-Driven Architecture).
    Desacopla la lógica de negocio (L2 Brain) de la infraestructura (L1 Nervous).
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.queue = asyncio.Queue()
        self._running = True
        self._worker_task = asyncio.create_task(self._process_queue())

    def subscribe(self, topic: str, callback: Callable):
        """Registra un suscriptor para un tópico específico."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Subscriptor registrado para el tópico: {topic}")

    async def publish(self, topic: str, data: Any):
        """Publica un evento unidireccional (Fire and Forget)."""
        await self.queue.put((topic, data, None))

    async def send_command(self, topic: str, data: Any) -> Any:
        """Envía un comando síncrono y espera el resultado (RPC)."""
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((topic, data, future))
        return await future

    async def _process_queue(self):
        while self._running:
            try:
                topic, data, future = await self.queue.get()
                if topic in self.subscribers:
                    for callback in self.subscribers[topic]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                result = await callback(data)
                            else:
                                result = callback(data)
                                
                            if future and not future.done():
                                future.set_result(result)
                        except Exception as e:
                            logger.error(f"Error procesando tópico '{topic}': {e}")
                            if future and not future.done():
                                future.set_exception(e)
                elif future and not future.done():
                    future.set_exception(ValueError(f"No hay suscriptores para el tópico: {topic}"))
                
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error crítico en el loop del Broker: {e}")

    async def shutdown(self):
        """Apagado gracioso del broker."""
        self._running = False
        self._worker_task.cancel()
        await asyncio.gather(self._worker_task, return_exceptions=True)
