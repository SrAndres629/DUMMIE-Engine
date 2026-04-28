import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger("mcp-proxy")


class MCPConnectionState(str, Enum):
    INIT = "INIT"
    WAIT_SERVER = "WAIT_SERVER"
    HANDSHAKE_OK = "HANDSHAKE_OK"
    DISCOVERY = "DISCOVERY"
    READY = "READY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class MCPProxyManager:
    """
    Gestiona el ciclo de vida y la comunicación con servidores MCP secundarios.
    Implementa el patrón Gateway de 2026.
    """
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.server_states: Dict[str, MCPConnectionState] = {}
        self.tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.last_accessed: Dict[str, float] = {}
        self._gc_task: Optional[asyncio.Task] = None
        self._load_config()


    def _load_config(self):
        """Carga la configuración de servidores desde el archivo JSON."""
        try:
            if not self.config_path.exists():
                logger.error(f"Config file not found: {self.config_path}")
                return
            
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.servers = data.get("mcpServers", {})
                logger.info(f"Loaded {len(self.servers)} servers from config.")
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")

    async def _garbage_collector_loop(self):
        """Monitorea inactividad y apaga servidores para liberar recursos (Idle Timeout)."""
        idle_timeout = 300 # 5 minutos
        while True:
            try:
                await asyncio.sleep(60) # Revisar cada minuto
                now = time.time()
                for server_name in list(self.active_processes.keys()):
                    last_used = self.last_accessed.get(server_name, 0)
                    if now - last_used > idle_timeout:
                        logger.info(f"🗑️ Garbage Collector: Apagando {server_name} por inactividad (>5m).")
                        if server_name not in self.locks:
                            self.locks[server_name] = asyncio.Lock()
                        
                        async with self.locks[server_name]:
                            proc = self.active_processes.get(server_name)
                            if proc:
                                try:
                                    proc.terminate()
                                except:
                                    pass
                                del self.active_processes[server_name]
                            self.server_states[server_name] = MCPConnectionState.INIT
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in GC loop: {e}")

    async def prefetch_server(self, server_name: str):
        """
        [Metacognición 2026] Arranca un servidor MCP en segundo plano.
        Reduce la latencia percibida al anticipar la necesidad del agente.
        """
        if server_name in self.servers and server_name not in self.active_processes:
            logger.info(f"Metacognitive Pre-fetching: Starting {server_name}")
            asyncio.create_task(self._ensure_process(server_name))

    async def get_tools_for_server(self, server_name: str) -> List[Dict[str, Any]]:
        """Interroga a un servidor para obtener su lista de herramientas."""
        await self._ensure_ready(server_name)
        return self.tool_cache.get(server_name, [])

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Ejecuta una herramienta en un servidor secundario."""
        if server_name not in self.servers:
            raise ValueError(f"Server '{server_name}' not found in registry.")

        server_cfg = self.servers[server_name]
        if server_cfg.get("disabled", False):
            raise ValueError(f"Server '{server_name}' is disabled.")
        if server_name not in self.locks:
            self.locks[server_name] = asyncio.Lock()

        self.last_accessed[server_name] = time.time()

        async with self.locks[server_name]:
            process = await self._ensure_ready(server_name)
            
            # Construir JSON-RPC Request
            try:
                result = await self._send_jsonrpc_request(
                    process,
                    "tools/call",
                    {"name": tool_name, "arguments": arguments},
                )
                # [Metacognición 2026] Entropy Filtering / Schema Homogenization
                # Evita saturar al LLM con metadatos técnicos innecesarios del sub-servidor
                return self._homogenize_response(result)
            except Exception as e:
                self.server_states[server_name] = MCPConnectionState.FAILED
                error_msg = str(e)
                logger.error(f"Error communicating with {server_name}: {error_msg}")
                
                # [Metacognición 2026] Gateway Diagnóstico
                # Buscamos si existe una lección previa para este error específico
                suggestion = self._lookup_lesson(error_msg)
                if suggestion:
                    logger.info(f"Gateway Diagnostic: Found relevant lesson for '{error_msg}'")
                    return {
                        "error": {
                            "code": -32000,
                            "message": f"Fallo en {server_name}: {error_msg}",
                            "data": {"suggestion": suggestion}
                        }
                    }
    
                # Si falla, limpiar proceso para reintento
                if server_name in self.active_processes:
                    del self.active_processes[server_name]
                raise

    async def _ensure_ready(self, server_name: str) -> asyncio.subprocess.Process:
        """Completa el handshake MCP antes de exponer tools/call."""
        # [FIX] Asegurar que el GC corra en el loop actual
        if self._gc_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._gc_task = loop.create_task(self._garbage_collector_loop())
                logger.info("MCP Proxy Garbage Collector started.")
            except RuntimeError:
                # Si no hay loop corriendo (raro aquí), lo intentará en la siguiente llamada
                pass

        if self.server_states.get(server_name) == MCPConnectionState.READY:
            proc = self.active_processes.get(server_name)
            if proc and proc.returncode is None:
                return proc

        process = await self._ensure_process(server_name)
        self.server_states[server_name] = MCPConnectionState.INIT

        try:
            self.server_states[server_name] = MCPConnectionState.WAIT_SERVER
            await self._send_jsonrpc_request(
                process,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "dummie-mcp-proxy", "version": "0.1.0"},
                },
                request_id=f"init-{server_name}-{os.urandom(4).hex()}",
            )

            self.server_states[server_name] = MCPConnectionState.HANDSHAKE_OK
            await self._send_jsonrpc_notification(process, "notifications/initialized", {})

            self.server_states[server_name] = MCPConnectionState.DISCOVERY
            tools_response = await self._send_jsonrpc_request(process, "tools/list", {})
            self.tool_cache[server_name] = tools_response.get("result", {}).get("tools", [])

            self.server_states[server_name] = MCPConnectionState.READY
            return process
        except Exception:
            self.server_states[server_name] = MCPConnectionState.FAILED
            raise

    async def _send_jsonrpc_request(
        self,
        process: asyncio.subprocess.Process,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": request_id or os.urandom(4).hex(),
            "method": method,
            "params": params,
        }
        input_data = json.dumps(payload) + "\n"
        process.stdin.write(input_data.encode())
        await process.stdin.drain()
        return await self._read_jsonrpc_response(process)

    async def _send_jsonrpc_notification(
        self,
        process: asyncio.subprocess.Process,
        method: str,
        params: Dict[str, Any],
    ) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
        input_data = json.dumps(payload) + "\n"
        process.stdin.write(input_data.encode())
        await process.stdin.drain()

    async def _read_jsonrpc_response(self, process: asyncio.subprocess.Process) -> Dict[str, Any]:
        # Leer respuesta (asumiendo una línea por respuesta para Stdio simple)
        # Nota: Esto es frágil si el servidor envía logs a stdout.
        response_data = await process.stdout.readline()
        if not response_data:
            raise RuntimeError("Server closed connection.")
        result = json.loads(response_data.decode())
        if "error" in result:
            raise RuntimeError(json.dumps(result["error"]))
        return result

    async def _ensure_process(self, server_name: str) -> asyncio.subprocess.Process:
        """Asegura que el proceso del servidor esté corriendo."""
        if server_name in self.active_processes:
            proc = self.active_processes[server_name]
            if proc.returncode is None:
                return proc

        cfg = self.servers[server_name]
        cmd = cfg["command"]
        args = cfg.get("args", [])
        env = os.environ.copy()
        if "env" in cfg:
            env.update(cfg["env"])

        # [SOVEREIGN SECURITY TOGGLE]
        aiwg_dir = Path(os.environ.get("DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.getcwd() + "/.aiwg")))
        state_file = aiwg_dir / "security_state"
        sandbox_mode = os.environ.get("DUMMIE_SANDBOX_MODE", "OFF").upper()
        
        if state_file.exists():
            with open(state_file, "r") as f:
                sandbox_mode = f.read().strip().upper()
        
        final_cmd = cmd
        final_args = args

        if sandbox_mode == "ON":
            logger.info(f"🛡️ Security Mode: HIGH (Sovereign Sandbox Active)")
            # Requisito: bwrap instalado. 
            # Configuramos un sandbox que permite red (share-net) pero aislada (loopback)
            # y monta el root_dir para que el servidor pueda trabajar.
            root_dir = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", os.getcwd()))
            
            bwrap_args = [
                "bwrap",
                "--unshare-all",
                "--share-net",
                "--loopback",
                "--dev", "/dev",
                "--proc", "/proc",
                "--tmpfs", "/tmp",
                "--ro-bind", "/usr", "/usr",
                "--ro-bind", "/lib", "/lib",
                "--ro-bind", "/lib64", "/lib64",
                "--ro-bind", "/bin", "/bin",
                "--ro-bind", "/sbin", "/sbin",
                "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
                "--bind", root_dir, root_dir,
                "--bind", os.path.expanduser("~"), os.path.expanduser("~"), # Necesario para npx/uv cache
                "--",
                cmd
            ]
            final_cmd = "bwrap"
            final_args = bwrap_args[1:] + args
        else:
            logger.info(f"🔓 Security Mode: LOW (Proximity Mode - Direct Execution)")

        logger.info(f"Starting MCP Server: {server_name} ({final_cmd})")
        try:
            process = await asyncio.create_subprocess_exec(
                final_cmd, *final_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
        except OSError as e:
            if e.errno == 1: # Operation not permitted
                logger.error(f"Sandbox Restriction: {server_name} failed with Errno 1.")
                raise RuntimeError(f"Sandbox Block: bwrap/RTM_NEWADDR. Sugerencia: Revisa 'unprivileged_userns_clone' o desactiva el sandbox.")
            raise
        
        # Manejo de logs en segundo plano (stderr)
        asyncio.create_task(self._log_stderr(server_name, process.stderr))
        
        self.active_processes[server_name] = process
        self.server_states.setdefault(server_name, MCPConnectionState.INIT)
        return process

    async def _log_stderr(self, name: str, stderr: asyncio.StreamReader):
        """Redirige los logs del servidor secundario al logger principal."""
        while True:
            line = await stderr.readline()
            if not line:
                break
            logger.info(f"[{name}] {line.decode().strip()}")

    async def shutdown(self):
        """Cierra todos los procesos activos y cancela tareas en background."""
        if hasattr(self, '_gc_task'):
            self._gc_task.cancel()
            
        for name, proc in self.active_processes.items():
            logger.info(f"Shutting down {name}...")
            try:
                proc.terminate()
                await proc.wait()
            except:
                pass
        self.active_processes.clear()

    def _homogenize_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia y estandariza la respuesta para consumo del agente LLM."""
        if "error" in raw_response:
            return raw_response
            
        # Extraer solo el contenido útil (Specs 2026: Low-Entropy Protocol)
        result = raw_response.get("result", {})
        if "content" in result:
            # Filtramos para quedarnos solo con el texto puro y resúmenes
            content = result["content"]
            clean_content = []
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if len(text) > 5000: # Causal Pruning automático
                        text = text[:5000] + "\n... [Output truncated by Gateway for context optimization]"
                    clean_content.append({"type": "text", "text": text})
            result["content"] = clean_content
            
        return {"jsonrpc": "2.0", "id": raw_response.get("id"), "result": result}

    def _lookup_lesson(self, error_msg: str) -> Optional[str]:
        """Busca en el historial de lecciones una solución para un error dado."""
        aiwg_dir = Path(os.environ.get("DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.getcwd() + "/.aiwg")))
        lessons_path = aiwg_dir / "memory" / "lessons.jsonl"
        if not lessons_path.exists():
            return None
            
        try:
            with open(lessons_path, "r") as f:
                # Leemos las últimas 50 lecciones (Causal Pruning)
                lines = f.readlines()[-50:]
                for line in reversed(lines):
                    lesson = json.loads(line)
                    # Búsqueda difusa simple
                    if lesson.get("issue", "").lower() in error_msg.lower() or error_msg.lower() in lesson.get("issue", "").lower():
                        return lesson.get("correction")
        except:
            pass
        return None
