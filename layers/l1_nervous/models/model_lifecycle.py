import time, asyncio, logging
from typing import Optional
from .adapters.base import BaseModelAdapter, ModelState
from .resource_monitor import ResourceMonitor, ModelPriority

logger = logging.getLogger("dummie-mcp.models.lifecycle")

LOAD_ORDER = {
    "embedding": 0,
    "reranker": 1,
    "llm": 2,
}


class PriorityItem:
    def __init__(
        self, adapter: BaseModelAdapter, priority: ModelPriority = ModelPriority.MEDIUM
    ):
        self.adapter = adapter
        self.priority = priority
        self.enqueued_at = time.time()


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
        self._priority_queue: list[PriorityItem] = []
        self._monitor = ResourceMonitor.get_instance()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._loading_lock = asyncio.Lock()

    def register(
        self, adapter: BaseModelAdapter, priority: ModelPriority = ModelPriority.MEDIUM
    ):
        self._models[adapter.spec.model_id] = adapter
        self._priority_queue.append(PriorityItem(adapter, priority))

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

    async def load_priority_queue(self):
        self._priority_queue.sort(
            key=lambda x: (
                x.priority.value,
                LOAD_ORDER.get(x.adapter.spec.model_type.value, 99),
            )
        )
        for item in self._priority_queue:
            if item.adapter.is_ready:
                continue
            ok, msg = self._monitor.can_load(
                item.adapter.spec.vram_mb, item.adapter.spec.ram_mb, item.priority
            )
            if not ok:
                logger.warning(f"Skipping {item.adapter.spec.model_id}: {msg}")
                continue
            async with self._loading_lock:
                logger.info(
                    f"Loading {item.adapter.spec.model_id} (vram={item.adapter.spec.vram_mb}MB, ram={item.adapter.spec.ram_mb}MB)"
                )
                await item.adapter.load()
                if item.adapter.is_ready:
                    release = self._monitor.snapshot()
                    logger.info(
                        f"  -> loaded OK. VRAM now: {release.vram_used_gb}/{release.vram_total_gb}GB"
                    )
                await asyncio.sleep(0.5)

    async def load_if_vram_available(
        self, adapter: BaseModelAdapter, priority: ModelPriority = ModelPriority.MEDIUM
    ):
        ok, msg = self._monitor.can_load(
            adapter.spec.vram_mb, adapter.spec.ram_mb, priority
        )
        if not ok:
            logger.warning(f"VRAM insufficient for {adapter.spec.model_id}: {msg}")
            if self._monitor._unified_memory:
                logger.info(
                    f"Unified memory active, loading anyway for {adapter.spec.model_id}"
                )
                await adapter.load()
            return False
        await adapter.load()
        return True

    async def ensure_loaded(self, model_id: str) -> Optional[BaseModelAdapter]:
        adapter = self._models.get(model_id)
        if not adapter:
            logger.error(f"Model {model_id} not registered")
            return None
        if adapter.is_ready:
            adapter.touch()
            return adapter
        await adapter.load()
        return adapter if adapter.is_ready else None

    async def unload(self, model_id: str):
        adapter = self._models.get(model_id)
        if adapter and adapter.is_ready:
            await adapter.close()

    async def unload_idle(self):
        for model_id, adapter in list(self._models.items()):
            ttl = self.ttls.get(adapter.spec.model_type.value, 300.0)
            if adapter.is_ready and adapter.idle_seconds > ttl:
                logger.info(
                    f"Unloading idle {model_id} (idle={adapter.idle_seconds:.0f}s)"
                )
                await adapter.close()

    async def unload_lowest_priority(self, exclude: list[str] = None):
        exclude = exclude or []
        loaded = [
            (m, a) for m, a in self._models.items() if a.is_ready and m not in exclude
        ]
        if not loaded:
            return
        loaded.sort(
            key=lambda x: (
                LOAD_ORDER.get(x[1].spec.model_type.value, 99),
                x[1].idle_seconds,
            )
        )
        mid, _ = loaded[0]
        await self.unload(mid)
        logger.info(f"Unloaded {mid} to free VRAM")

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
        for adapter in list(self._models.values()):
            await adapter.close()
        self._models.clear()
        self._priority_queue.clear()

    def summary(self) -> dict:
        return {
            model_id: {
                "state": adapter.state.value,
                "type": adapter.spec.model_type.value,
                "priority": adapter.spec.priority,
                "vram_mb": adapter.spec.vram_mb,
                "ram_mb": adapter.spec.ram_mb,
                "idle_seconds": round(adapter.idle_seconds, 1),
                "load_count": adapter.metrics.load_count,
                "total_inference_ms": round(adapter.metrics.total_inference_ms, 0),
                "error_count": adapter.metrics.error_count,
            }
            for model_id, adapter in self._models.items()
        }

    def queue_status(self) -> list[dict]:
        return [
            {
                "model_id": item.adapter.spec.model_id,
                "type": item.adapter.spec.model_type.value,
                "priority": item.priority.name,
                "loaded": item.adapter.is_ready,
                "queued_seconds_ago": round(time.time() - item.enqueued_at, 1),
            }
            for item in self._priority_queue
        ]
