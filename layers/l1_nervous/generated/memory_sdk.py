from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para memory
# NO EDITAR DIRECTAMENTE.

class MemoryClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def create_entities(self, **kwargs) -> Any:
        """Create multiple new entities in the knowledge graph"""
        return await self.proxy.call_tool('memory', 'create_entities', kwargs)

    async def create_relations(self, **kwargs) -> Any:
        """Create multiple new relations between entities in the knowledge graph. Relations should be in active voice"""
        return await self.proxy.call_tool('memory', 'create_relations', kwargs)

    async def add_observations(self, **kwargs) -> Any:
        """Add new observations to existing entities in the knowledge graph"""
        return await self.proxy.call_tool('memory', 'add_observations', kwargs)

    async def delete_entities(self, **kwargs) -> Any:
        """Delete multiple entities and their associated relations from the knowledge graph"""
        return await self.proxy.call_tool('memory', 'delete_entities', kwargs)

    async def delete_observations(self, **kwargs) -> Any:
        """Delete specific observations from entities in the knowledge graph"""
        return await self.proxy.call_tool('memory', 'delete_observations', kwargs)

    async def delete_relations(self, **kwargs) -> Any:
        """Delete multiple relations from the knowledge graph"""
        return await self.proxy.call_tool('memory', 'delete_relations', kwargs)

    async def read_graph(self, **kwargs) -> Any:
        """Read the entire knowledge graph"""
        return await self.proxy.call_tool('memory', 'read_graph', kwargs)

    async def search_nodes(self, **kwargs) -> Any:
        """Search for nodes in the knowledge graph based on a query"""
        return await self.proxy.call_tool('memory', 'search_nodes', kwargs)

    async def open_nodes(self, **kwargs) -> Any:
        """Open specific nodes in the knowledge graph by their names"""
        return await self.proxy.call_tool('memory', 'open_nodes', kwargs)
