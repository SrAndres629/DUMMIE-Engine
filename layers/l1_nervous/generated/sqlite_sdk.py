from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para sqlite
# NO EDITAR DIRECTAMENTE.

class SqliteClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def read_query(self, **kwargs) -> Any:
        """Execute a SELECT query on the SQLite database"""
        return await self.proxy.call_tool('sqlite', 'read_query', kwargs)

    async def write_query(self, **kwargs) -> Any:
        """Execute an INSERT, UPDATE, or DELETE query on the SQLite database"""
        return await self.proxy.call_tool('sqlite', 'write_query', kwargs)

    async def create_table(self, **kwargs) -> Any:
        """Create a new table in the SQLite database"""
        return await self.proxy.call_tool('sqlite', 'create_table', kwargs)

    async def list_tables(self, **kwargs) -> Any:
        """List all tables in the SQLite database"""
        return await self.proxy.call_tool('sqlite', 'list_tables', kwargs)

    async def describe_table(self, **kwargs) -> Any:
        """Get the schema information for a specific table"""
        return await self.proxy.call_tool('sqlite', 'describe_table', kwargs)

    async def append_insight(self, **kwargs) -> Any:
        """Add a business insight to the memo"""
        return await self.proxy.call_tool('sqlite', 'append_insight', kwargs)
