import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("mcp-proxy")

class MCPProxyManager:
    """
    Gestiona el ciclo de vida y la comunicación con servidores MCP secundarios.
    Implementa el patrón Gateway de 2026.
    """
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
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
        # En una implementación real, esto ejecutaría 'list_tools' vía JSON-RPC.
        # Por ahora, simulamos o devolvemos un esquema básico si ya lo conocemos.
        # Para 2026, lo ideal es tener un caché de capacidades.
        response = await self.call_tool(server_name, "list_tools", {})
        return response.get("tools", [])

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Ejecuta una herramienta en un servidor secundario."""
        if server_name not in self.servers:
            raise ValueError(f"Server '{server_name}' not found in registry.")

        server_cfg = self.servers[server_name]
        if server_cfg.get("disabled", False):
            raise ValueError(f"Server '{server_name}' is disabled.")

        # Obtener o iniciar proceso
        process = await self._ensure_process(server_name)
        
        # Construir JSON-RPC Request
        request_id = os.urandom(4).hex()
        # Nota: 'list_tools' es una operación especial en MCP, 
        # pero aquí usamos el mismo canal para simplicidad.
        method = "tools/call" if tool_name != "list_tools" else "tools/list"
        
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": {
                "name": tool_name,
                "arguments": arguments
            } if tool_name != "list_tools" else {}
        }

        try:
            input_data = json.dumps(payload) + "\n"
            process.stdin.write(input_data.encode())
            await process.stdin.drain()

            # Leer respuesta (asumiendo una línea por respuesta para Stdio simple)
            # Nota: Esto es frágil si el servidor envía logs a stdout. 
            # Los servidores MCP bien implementados envían logs a stderr.
            response_data = await process.stdout.readline()
            if not response_data:
                raise RuntimeError(f"Server '{server_name}' closed connection.")
            
            result = json.loads(response_data.decode())
            
            # [Metacognición 2026] Entropy Filtering / Schema Homogenization
            # Evita saturar al LLM con metadatos técnicos innecesarios del sub-servidor
            return self._homogenize_response(result)
        except Exception as e:
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

        logger.info(f"Starting MCP Server: {server_name} ({cmd})")
        try:
            process = await asyncio.create_subprocess_exec(
                cmd, *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
        except OSError as e:
            if e.errno == 1: # Operation not permitted
                logger.error(f"Sandbox Restriction: {server_name} failed with Errno 1.")
                raise RuntimeError(f"Sandbox Block: bwrap/RTM_NEWADDR. Sugerencia: Revisa 'unprivileged_userns_clone' o desactiva el sandbox del runner.")
            raise
        
        # Manejo de logs en segundo plano (stderr)
        asyncio.create_task(self._log_stderr(server_name, process.stderr))
        
        self.active_processes[server_name] = process
        return process

    async def _log_stderr(self, name: str, stderr: asyncio.StreamReader):
        """Redirige los logs del servidor secundario al logger principal."""
        while True:
            line = await stderr.readline()
            if not line:
                break
            logger.info(f"[{name}] {line.decode().strip()}")

    async def shutdown(self):
        """Cierra todos los procesos activos."""
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
        lessons_path = Path(os.environ.get("DUMMIE_AIWG_DIR", "/home/jorand/Escritorio/DUMMIE Engine/.aiwg")) / "memory" / "lessons.jsonl"
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
