import asyncio
import logging
import time
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
from enum import Enum

from layers.l1_nervous.mcp_transport import MCPTransport
from layers.l1_nervous.mcp_registry import MCPRegistry

logger = logging.getLogger("mcp-proxy")


class MCPConnectionState(str, Enum):
    INIT = "INIT"
    READY = "READY"
    FAILED = "FAILED"


class MCPProxyManager:
    """
    [L1_NERVOUS] Orquestador de Proxy MCP.
    Delega el transporte a MCPTransport y el registro a MCPRegistry.
    Incluye circuit breaker con exponential backoff para respawn.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.registry = MCPRegistry(Path(config_path))
        self.transport = MCPTransport()
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.server_states: Dict[str, MCPConnectionState] = {}
        self.last_accessed: Dict[str, float] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._gc_task: Optional[asyncio.Task] = None
        # Circuit breaker state
        self._retry_counts: Dict[str, int] = {}
        self._retry_backoff: Dict[
            str, float
        ] = {}  # próxima ventana permitida (time.time)
        self._max_retries = 5
        self._backoff_base = 4.0  # segundos, se duplica cada intento (más agresivo)
        self._prewarmed = False

        self._start_prewarming()

    def _start_prewarming(self):
        hot = os.environ.get("DUMMIE_PREWARM", "")
        if not hot:
            return
        servers = [s.strip() for s in hot.split(",") if s.strip()]
        if not servers:
            return
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._prewarm(servers))
        except RuntimeError:
            pass

    async def _prewarm(self, servers: list[str]):
        if self._prewarmed:
            return
        self._prewarmed = True
        for name in servers:
            if name in self.registry.servers:
                try:
                    await self._ensure_ready(name)
                    logger.info("pre-warmed: %s", name)
                except Exception as e:
                    logger.warning("pre-warm failed for %s: %s", name, e)

    async def get_tools_for_server(self, server_name: str) -> List[Dict[str, Any]]:
        if server_name not in self.locks:
            self.locks[server_name] = asyncio.Lock()
        async with self.locks[server_name]:
            await self._ensure_ready(server_name)
            return self.registry.get_tools(server_name)

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        cfg = self.registry.get_server_config(server_name)
        if not cfg:
            raise ValueError(
                f"Server '{server_name}' not found in gateway config. "
                f"Sugerencia: Añádelo a dummie_gateway_config.json en la sección mcpServers."
            )

        # [Somatic Sensor-First Injection] Runtime Guard for File Reading
        if server_name == "filesystem" and tool_name in {"read_text_file", "read_file"}:
            try:
                from layers.l2_brain.sensor_first_guard import SensorFirstGuard
                from layers.l2_brain.metagateway_policy import PolicyDecision

                # In a real environment, we'd pull purpose and context from context_token/telemetry.
                # For somatic enforcement at this level, we enforce a strict baseline if it's a blind read.
                # We assume we don't have gateway info here unless passed via arguments (which we don't standardly do yet),
                # but we can log the evaluation. For now, we evaluate in WARN mode to track without breaking everything,
                # unless explicitly configured otherwise.
                guard = SensorFirstGuard(mode=PolicyDecision.WARN)

                # Check if this read feels like a concept discovery (e.g. no specific line target)
                purpose = (
                    "concept_discovery"
                    if "head" not in arguments and "tail" not in arguments
                    else "line_confirmation"
                )

                eval_result = guard.evaluate_direct_read(
                    purpose=purpose,
                    semantic_search_attempted=arguments.get(
                        "_semantic_search_attempted", False
                    ),
                    gateway_attempted=arguments.get("_gateway_attempted", False),
                )

                if eval_result["decision"] == "BLOCK":
                    logger.error(
                        f"[Sensor-First] BLOCKED read request for {arguments.get('path', 'unknown')}: {eval_result['reason']}"
                    )
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error: Sensor-First policy blocked this request: {eval_result['reason']}",
                                }
                            ]
                        },
                    }
                elif eval_result["decision"] == "WARN":
                    logger.warning(
                        f"[Sensor-First] WARNING for read request {arguments.get('path', 'unknown')}: {eval_result['reason']}"
                    )

            except ImportError as e:
                logger.debug(f"[Sensor-First] Guard not available at proxy level: {e}")
            except Exception as e:
                logger.error(f"[Sensor-First] Guard evaluation failed: {e}")

        self.last_accessed[server_name] = time.time()
        if server_name not in self.locks:
            self.locks[server_name] = asyncio.Lock()

        async with self.locks[server_name]:
            proc = await self._ensure_ready(server_name)
            result = await self.transport.send_request(
                proc,
                "tools/call",
                {"name": tool_name, "arguments": arguments},
                server_name=server_name,
            )
            return self._homogenize_response(result)

    async def _ensure_ready(self, server_name: str) -> asyncio.subprocess.Process:
        now = time.time()

        # Circuit breaker: si estamos en backoff, esperar
        if self._retry_backoff.get(server_name, 0) > now:
            wait = self._retry_backoff[server_name] - now
            raise ConnectionError(
                f"Server '{server_name}' en circuit breaker. "
                f"Reintentar en {wait:.1f}s "
                f"(intento {self._retry_counts.get(server_name, 0)}/{self._max_retries}). "
                f"Sugerencia: Verifica que el binario/comando esté instalado y accesible en el PATH."
            )

        if self.server_states.get(server_name) == MCPConnectionState.READY:
            proc = self.active_processes.get(server_name)
            if proc and proc.returncode is None:
                self._retry_counts[server_name] = 0
                return proc

        cfg = self.registry.get_server_config(server_name)
        try:
            proc = await self.transport.spawn_process(server_name, cfg)
        except FileNotFoundError as e:
            self.server_states[server_name] = MCPConnectionState.FAILED
            raise FileNotFoundError(
                f"Server '{server_name}' command not found: {e}. "
                f"Sugerencia: Instala el binario requerido (npx, uvx, etc.) o verifica el PATH."
            ) from e
        except Exception as e:
            count = self._retry_counts.get(server_name, 0) + 1
            self._retry_counts[server_name] = count
            if count >= self._max_retries:
                backoff = self._backoff_base**self._max_retries
                self._retry_backoff[server_name] = time.time() + backoff
                self.server_states[server_name] = MCPConnectionState.FAILED
                raise ConnectionError(
                    f"Server '{server_name}' falló {count} veces consecutivas. "
                    f"Circuit breaker activo por {backoff:.0f}s. "
                    f"Sugerencia: Revisa dummie_gateway_config.json para '{server_name}' "
                    f"y verifica que el comando/args sean correctos."
                ) from e
            backoff = self._backoff_base**count
            self._retry_backoff[server_name] = time.time() + backoff
            logger.warning(
                f"Server '{server_name}' falló (intento {count}/{self._max_retries}), "
                f"backoff {backoff:.1f}s"
            )
            raise

        self.active_processes[server_name] = proc
        self._retry_counts[server_name] = 0

        # Handshake
        await self.transport.send_request(
            proc,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "dummie-proxy", "version": "1.0"},
            },
            server_name=server_name,
        )
        await self.transport.send_notification(proc, "notifications/initialized", {})

        # Discovery
        tools_resp = await self.transport.send_request(
            proc, "tools/list", {}, server_name=server_name
        )
        self.registry.update_tools(
            server_name, tools_resp.get("result", {}).get("tools", [])
        )

        self.server_states[server_name] = MCPConnectionState.READY
        return proc

    def _homogenize_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        result = raw.get("result", {})
        if "content" in result:
            for item in result["content"]:
                if item.get("type") == "text" and len(item.get("text", "")) > 5000:
                    item["text"] = item["text"][:5000] + "\n[Truncated]"
        return {"jsonrpc": "2.0", "result": result}

    async def shutdown(self):
        """Cierre limpio y ordenado de todos los subprocesos MCP delegando al transporte."""
        for name, proc in self.active_processes.items():
            try:
                logger.debug(f"Shutting down server: {name}")
                await self.transport.close_connection(proc, server_name=name)
            except Exception as e:
                logger.error(f"Failed to shut down server {name}: {e}")
        self.active_processes.clear()
        self.server_states.clear()
