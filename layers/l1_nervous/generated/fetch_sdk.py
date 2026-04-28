from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para fetch
# NO EDITAR DIRECTAMENTE.

class FetchClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def fetch(self, **kwargs) -> Any:
        """Fetches a URL from the internet and optionally extracts its contents as markdown.  Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that."""
        return await self.proxy.call_tool('fetch', 'fetch', kwargs)
