import asyncio
import json
import logging
import os
import re
import shutil
from typing import Any, Dict, Optional

logger = logging.getLogger("mcp-transport")

_BINARY_CACHE = {}


def _expand_env(s: str) -> str:
    """Expands $VAR and ${VAR} env vars (Python expandvars only handles $VAR)."""

    def _replacer(m):
        var = m.group(1) or m.group(2)
        return os.environ.get(var, m.group(0))

    return re.sub(r"\$\{(\w+)\}|\$(\w+)", _replacer, s)


def _resolve_binary(cmd: str) -> str:
    if cmd not in _BINARY_CACHE:
        resolved = shutil.which(cmd)
        _BINARY_CACHE[cmd] = resolved
    return _BINARY_CACHE[cmd]


class MCPTransport:
    """
    [L1_NERVOUS] Transport: Gestión atómica mediante colas y TaskGroups.
    Soporta múltiples sub-servidores concurrentes con colas independientes.
    """

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._reader_tasks: Dict[str, asyncio.Task] = {}

    async def spawn_process(
        self, server_name: str, config: Dict[str, Any]
    ) -> asyncio.subprocess.Process:
        cmd = _expand_env(config["command"])
        args = [
            _expand_env(a) if isinstance(a, str) else a for a in config.get("args", [])
        ]
        env = os.environ.copy()
        env.update(
            {
                key: _expand_env(value) if isinstance(value, str) else value
                for key, value in config.get("env", {}).items()
            }
        )

        resolved = _resolve_binary(cmd)
        if not resolved:
            raise FileNotFoundError(
                f"Binario no encontrado para server '{server_name}': '{cmd}' no está en PATH. "
                f"Instálalo con: npx -y {cmd} (si es un paquete npm) "
                f"o asegúrate de que esté disponible en el sistema."
            )

        proc = await asyncio.create_subprocess_exec(
            resolved,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        self._queues[server_name] = asyncio.Queue()
        self._reader_tasks[server_name] = asyncio.create_task(
            self._reader_worker(server_name, proc.stdout)
        )
        return proc

    async def _reader_worker(self, server_name: str, stream: asyncio.StreamReader):
        try:
            queue = self._queues.get(server_name)
            while not stream.at_eof():
                line = await stream.readline()
                if line and queue:
                    await queue.put(line)
        except Exception as e:
            logger.debug(f"Reader worker '{server_name}' stopped: {e}")

    def _get_queue(self, server_name: str) -> asyncio.Queue:
        return self._queues.setdefault(server_name, asyncio.Queue())

    async def send_request(
        self,
        process: asyncio.subprocess.Process,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
        server_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": request_id or os.urandom(4).hex(),
            "method": method,
            "params": params,
        }
        process.stdin.write((json.dumps(payload) + "\n").encode())
        await process.stdin.drain()
        return await self.read_response(process, server_name=server_name)

    async def send_notification(
        self, process: asyncio.subprocess.Process, method: str, params: Dict[str, Any]
    ) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        process.stdin.write((json.dumps(payload) + "\n").encode())
        await process.stdin.drain()

    async def read_response(
        self, process: asyncio.subprocess.Process, server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        queue = self._get_queue(server_name or "_default")
        line = await queue.get()
        line_str = line.decode().strip()
        while not (line_str.startswith("{") or line_str.startswith("Content-Length:")):
            line = await queue.get()
            line_str = line.decode().strip()
        if line_str.startswith("Content-Length:"):
            length = int(line_str.split(":")[1].strip())
            await queue.get()
            body = await queue.get()
            return json.loads(body.decode())
        return json.loads(line_str)

    async def close_connection(
        self, process: asyncio.subprocess.Process, server_name: Optional[str] = None
    ):
        """Cierre estructurado: Cancela reader -> Cierra stdin -> Termina proceso."""
        sn = server_name or "_default"
        task = self._reader_tasks.get(sn)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self._reader_tasks.pop(sn, None)
        self._queues.pop(sn, None)

        if process.stdin:
            try:
                process.stdin.close()
                await process.stdin.wait_closed()
            except:
                pass

        if process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=3.0)
            except:
                process.kill()
                await process.wait()
