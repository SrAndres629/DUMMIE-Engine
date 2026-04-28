from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para ctags
# NO EDITAR DIRECTAMENTE.

class CtagsClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def find_symbol(self, **kwargs) -> Any:
        """Search for function/class/variable definitions by name in the codebase. Returns file path and line number. Faster and more precise than grep."""
        return await self.proxy.call_tool('ctags', 'find_symbol', kwargs)

    async def find_references(self, **kwargs) -> Any:
        """Find all usages/call sites of a symbol across the codebase using ripgrep. Use this to answer "where is X called/used?" — complements find_symbol which answers "where is X defined?"."""
        return await self.proxy.call_tool('ctags', 'find_references', kwargs)

    async def refresh_tags(self, **kwargs) -> Any:
        """Regenerate the ctags index. Run this after significant code changes, new files, or branch switches."""
        return await self.proxy.call_tool('ctags', 'refresh_tags', kwargs)
