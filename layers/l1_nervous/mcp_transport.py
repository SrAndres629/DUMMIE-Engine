import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, Optional, List
from pathlib import Path

logger = logging.getLogger("mcp-transport")

class MCPTransport:
    """
    [L1_NERVOUS] Maneja la comunicación física JSON-RPC sobre Stdio con Sandboxing.
    """
    async def spawn_process(self, server_name: str, config: Dict[str, Any]) -> asyncio.subprocess.Process:
        cmd = config["command"]
        args = config.get("args", [])
        env = os.environ.copy()
        if "env" in config:
            env.update(config["env"])

        # Sovereign Sandbox Logic (Simplified for modular use)
        sandbox_mode = os.environ.get("DUMMIE_SANDBOX_MODE", "OFF").upper()
        
        final_cmd = cmd
        final_args = args

        if sandbox_mode == "ON":
            root_dir = os.environ.get("DUMMIE_ROOT", os.getcwd())
            bwrap_args = ["bwrap", "--unshare-all", "--share-net", "--loopback", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64", "--ro-bind", "/bin", "/bin", "--ro-bind", "/sbin", "/sbin", "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf", "--bind", root_dir, root_dir, "--bind", os.path.expanduser("~"), os.path.expanduser("~"), "--", cmd]
            final_cmd = "bwrap"
            final_args = bwrap_args[1:] + args

        logger.debug(f"Spawning MCP Process: {server_name}")
        return await asyncio.create_subprocess_exec(
            final_cmd, *final_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

    async def send_request(self, process: asyncio.subprocess.Process, method: str, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": request_id or os.urandom(4).hex(), "method": method, "params": params}
        process.stdin.write((json.dumps(payload) + "\n").encode())
        await process.stdin.drain()
        return await self.read_response(process)

    async def send_notification(self, process: asyncio.subprocess.Process, method: str, params: Dict[str, Any]) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        process.stdin.write((json.dumps(payload) + "\n").encode())
        await process.stdin.drain()

    async def read_response(self, process: asyncio.subprocess.Process) -> Dict[str, Any]:
        line = await process.stdout.readline()
        if not line: raise RuntimeError("Server closed connection.")
        
        line_str = line.decode().strip()
        if line_str.startswith("Content-Length:"):
            length = int(line_str.split(":")[1].strip())
            await process.stdout.readline()
            body = await process.stdout.readexactly(length)
            return json.loads(body.decode())
        
        if line_str.startswith("{"):
            return json.loads(line_str)
            
        # Skip logs and find JSON
        while not (line_str.startswith("{") or line_str.startswith("Content-Length:")):
            line = await process.stdout.readline()
            if not line: raise RuntimeError("Connection lost during log skip.")
            line_str = line.decode().strip()
        
        if line_str.startswith("Content-Length:"):
            length = int(line_str.split(":")[1].strip())
            await process.stdout.readline()
            body = await process.stdout.readexactly(length)
            return json.loads(body.decode())
        return json.loads(line_str)
