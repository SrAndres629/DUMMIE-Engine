import time, asyncio, logging
from typing import Optional
from .adapters.base import BaseModelAdapter, ModelState

logger = logging.getLogger("dummie-mcp.models.lifecycle")


class ModelLifecycle:
    def __init__(
        self,
        ttl_embedding: float = 600.0,
        ttl_llm: float = 300.0,
        ttl_reranker: float = 600.0,
    ):
        self.ttls = {
            "embedding": ttl_embedding,
            "llm": ttl_llm,
            "reranker": ttl_reranker,
        }
        self._models: dict[str, BaseModelAdapter] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def register(self, adapter: BaseModelAdapter):
        self._models[adapter.spec.model_id] = adapter

    def get(self, model_id: str) -> Optional[BaseModelAdapter]:
        adapter = self._models.get(model_id)
        if adapter:
            adapter.touch()
        return adapter

    def get_ready(self, model_id: str) -> Optional[BaseModelAdapter]:
        adapter = self.get(model_id)
        if adapter and adapter.is_ready:
            return adapter
        return None

    def get_all_loaded(self) -> list[BaseModelAdapter]:
        return [m for m in self._models.values() if m.is_ready]

    async def unload_idle(self):
        for model_id, adapter in list(self._models.items()):
            ttl = self.ttls.get(adapter.spec.model_type.value, 300.0)
            if adapter.is_ready and adapter.idle_seconds > ttl:
                logger.info(
                    f"Unloading idle model {model_id} (idle={adapter.idle_seconds:.0f}s > ttl={ttl}s)"
                )
                await adapter.close()
                del self._models[model_id]

    def start_cleanup_loop(self, interval: float = 60.0):
        async def _loop():
            while True:
                await asyncio.sleep(interval)
                try:
                    await self.unload_idle()
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")

        self._cleanup_task = asyncio.create_task(_loop())

    async def stop(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
        for model_id, adapter in list(self._models.items()):
            await adapter.close()
        self._models.clear()

    def summary(self) -> dict:
        return {
            model_id: {
                "state": adapter.state.value,
                "type": adapter.spec.model_type.value,
                "idle_seconds": round(adapter.idle_seconds, 1),
                "load_count": adapter.metrics.load_count,
                "total_inference_ms": round(adapter.metrics.total_inference_ms, 0),
                "error_count": adapter.metrics.error_count,
            }
            for model_id, adapter in self._models.items()
        }
