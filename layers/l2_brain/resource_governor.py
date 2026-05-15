import os
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("dummie.resource_governor")

class ResourceGovernor:
    """
    [L2_BRAIN] Observador Autonómico de Recursos.
    Monitorea los Cgroups v2 y la presión del SO para adaptar la concurrencia del DUMMIE Engine.
    """
    def __init__(self, threshold_warning: float = 0.8, threshold_critical: float = 0.95):
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.last_active_time = asyncio.get_event_loop().time()
        self.idle_timeout_seconds = 600  # 10 minutes

    def record_activity(self):
        self.last_active_time = asyncio.get_event_loop().time()

    async def _read_cgroup_memory_ratio(self) -> float:
        # En producción esto lee /sys/fs/cgroup/.../memory.current y memory.max
        # Por seguridad y portabilidad, simulamos esto como un stub por ahora.
        return 0.5

    async def _unload_ollama(self):
        logger.info("[GOVERNOR] Unloading Ollama to reclaim VRAM due to idle timeout.")
        try:
            # Requires passwordless sudo or user systemd control over ollama
            proc = await asyncio.create_subprocess_exec(
                "systemctl", "--user", "stop", "ollama",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            logger.error(f"[GOVERNOR] Failed to unload Ollama: {e}")

    async def evaluate_system_health(self) -> Dict[str, Any]:
        ratio = await self._read_cgroup_memory_ratio()
        
        if ratio >= self.threshold_critical:
            logger.warning(f"[GOVERNOR] Memory pressure CRITICAL ({ratio*100:.1f}%). Throttling concurrency to 1.")
            return {"status": "CRITICAL", "recommended_concurrency": 1, "action": "THROTTLE"}
        elif ratio >= self.threshold_warning:
            logger.warning(f"[GOVERNOR] Memory pressure WARNING ({ratio*100:.1f}%). Reducing concurrency to 3.")
            return {"status": "WARNING", "recommended_concurrency": 3, "action": "REDUCE"}
        else:
            return {"status": "HEALTHY", "recommended_concurrency": 5, "action": "NONE"}

    async def evaluate_idle_timeout(self):
        elapsed = asyncio.get_event_loop().time() - self.last_active_time
        if elapsed > self.idle_timeout_seconds:
            await self._unload_ollama()
            # Reset timer so we don't spam the stop command
            self.last_active_time = asyncio.get_event_loop().time()
