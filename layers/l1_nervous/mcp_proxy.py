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
    """
    def __init__(self, config_path: str):
        self.registry = MCPRegistry(Path(config_path))
        self.transport = MCPTransport()
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.server_states: Dict[str, MCPConnectionState] = {}
        self.last_accessed: Dict[str, float] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._gc_task: Optional[asyncio.Task] = None

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        cfg = self.registry.get_server_config(server_name)
        if not cfg: raise ValueError(f"Server {server_name} not found.")
        
        self.last_accessed[server_name] = time.time()
        if server_name not in self.locks: self.locks[server_name] = asyncio.Lock()
        
        async with self.locks[server_name]:
            proc = await self._ensure_ready(server_name)
            result = await self.transport.send_request(proc, "tools/call", {"name": tool_name, "arguments": arguments})
            return self._homogenize_response(result)

    async def _ensure_ready(self, server_name: str) -> asyncio.subprocess.Process:
        if self.server_states.get(server_name) == MCPConnectionState.READY:
            proc = self.active_processes.get(server_name)
            if proc and proc.returncode is None: return proc

        cfg = self.registry.get_server_config(server_name)
        proc = await self.transport.spawn_process(server_name, cfg)
        self.active_processes[server_name] = proc
        
        # Handshake
        await self.transport.send_request(proc, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "dummie-proxy", "version": "1.0"}})
        await self.transport.send_notification(proc, "notifications/initialized", {})
        
        # Discovery
        tools_resp = await self.transport.send_request(proc, "tools/list", {})
        self.registry.update_tools(server_name, tools_resp.get("result", {}).get("tools", []))
        
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
        for name, proc in self.active_processes.items():
            try: proc.terminate()
            except: pass
        self.active_processes.clear()
