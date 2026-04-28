from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para genkit-mcp-server
# NO EDITAR DIRECTAMENTE.

class GenkitMcpServerClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def list_genkit_docs(self, **kwargs) -> Any:
        """Use this to see a list of available Genkit documentation files. Returns `filePaths` that can be passed to `read_genkit_docs`."""
        return await self.proxy.call_tool('genkit-mcp-server', 'list_genkit_docs', kwargs)

    async def search_genkit_docs(self, **kwargs) -> Any:
        """Use this to search the Genkit documentation using keywords. Returns ranked results with `filePaths` for `read_genkit_docs`. Warning: Generic terms (e.g. "the", "and") may return false positives; use specific technical terms (e.g. "rag", "firebase", "context")."""
        return await self.proxy.call_tool('genkit-mcp-server', 'search_genkit_docs', kwargs)

    async def read_genkit_docs(self, **kwargs) -> Any:
        """Use this to read the full content of specific Genkit documentation files. You must provide `filePaths` from the list/search tools."""
        return await self.proxy.call_tool('genkit-mcp-server', 'read_genkit_docs', kwargs)

    async def get_usage_guide(self, **kwargs) -> Any:
        """Use this tool to look up the official Genkit usage guide, including project setup instructions and API best practices. ALWAYS call this before implementing Genkit features."""
        return await self.proxy.call_tool('genkit-mcp-server', 'get_usage_guide', kwargs)

    async def list_flows(self, **kwargs) -> Any:
        """Use this to discover available Genkit flows or inspect the input schema of Genkit flows to know how to successfully call them."""
        return await self.proxy.call_tool('genkit-mcp-server', 'list_flows', kwargs)

    async def run_flow(self, **kwargs) -> Any:
        """Runs the flow with the provided input"""
        return await self.proxy.call_tool('genkit-mcp-server', 'run_flow', kwargs)

    async def get_trace(self, **kwargs) -> Any:
        """Returns the trace details."""
        return await self.proxy.call_tool('genkit-mcp-server', 'get_trace', kwargs)

    async def start_runtime(self, **kwargs) -> Any:
        """Use this to start a Genkit runtime process (This is typically the entry point to the users app). Once started, the runtime will be picked up by the `genkit start` command to power the Dev UI features like model and flow playgrounds. The inputSchema for this tool matches the function prototype for `NodeJS.child_process.spawn`.                Examples:          {command: "go", args: ["run", "main.go"]}         {command: "npm", args: ["run", "dev"]}         {command: "npm", args: ["run", "dev"], projectRoot: "path/to/project"}"""
        return await self.proxy.call_tool('genkit-mcp-server', 'start_runtime', kwargs)

    async def kill_runtime(self, **kwargs) -> Any:
        """Use this to kill an existing runtime that was started using the `start_runtime` tool"""
        return await self.proxy.call_tool('genkit-mcp-server', 'kill_runtime', kwargs)

    async def restart_runtime(self, **kwargs) -> Any:
        """Use this to restart an existing runtime that was started using the `start_runtime` tool"""
        return await self.proxy.call_tool('genkit-mcp-server', 'restart_runtime', kwargs)
