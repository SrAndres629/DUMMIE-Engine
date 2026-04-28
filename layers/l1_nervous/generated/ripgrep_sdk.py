from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para ripgrep
# NO EDITAR DIRECTAMENTE.

class RipgrepClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def search(self, **kwargs) -> Any:
        """Search files for patterns using ripgrep (rg)"""
        return await self.proxy.call_tool('ripgrep', 'search', kwargs)

    async def advanced_search(self, **kwargs) -> Any:
        """Advanced search with ripgrep with more options"""
        return await self.proxy.call_tool('ripgrep', 'advanced-search', kwargs)

    async def count_matches(self, **kwargs) -> Any:
        """Count matches in files using ripgrep"""
        return await self.proxy.call_tool('ripgrep', 'count-matches', kwargs)

    async def list_files(self, **kwargs) -> Any:
        """List files that would be searched by ripgrep without actually searching them"""
        return await self.proxy.call_tool('ripgrep', 'list-files', kwargs)

    async def list_file_types(self, **kwargs) -> Any:
        """List all supported file types in ripgrep"""
        return await self.proxy.call_tool('ripgrep', 'list-file-types', kwargs)
