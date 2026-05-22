import asyncio
import logging
from typing import Dict, Optional
from layers.l2_brain.infrastructure.gateway_contract import TaskExecution

logger = logging.getLogger("brain.supervisor")

class ProcessSupervisor:
    """
    [L2_BRAIN] Supervisor Soberano.
    Responsable único de la gestión del ciclo de vida de los procesos MCP.
    """
    def __init__(self):
        self._managed_processes: Dict[str, asyncio.subprocess.Process] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def ensure_active(self, server_id: str, spawn_fn) -> asyncio.subprocess.Process:
        if server_id not in self._locks:
            self._locks[server_id] = asyncio.Lock()
            
        async with self._locks[server_id]:
            proc = self._managed_processes.get(server_id)
            if proc and proc.returncode is None:
                return proc
            
            logger.info(f"Supervisor: Spawn solicitado para {server_id}")
            proc = await spawn_fn()
            self._managed_processes[server_id] = proc
            return proc

    async def terminate_all(self):
        for s_id, proc in self._managed_processes.items():
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=2.0)
            except:
                proc.kill()
        self._managed_processes.clear()
        logger.info("Supervisor: Todos los procesos terminados.")
