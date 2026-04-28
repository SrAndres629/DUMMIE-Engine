from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para time
# NO EDITAR DIRECTAMENTE.

class TimeClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def get_current_time(self, **kwargs) -> Any:
        """Get current time in a specific timezones"""
        return await self.proxy.call_tool('time', 'get_current_time', kwargs)

    async def convert_time(self, **kwargs) -> Any:
        """Convert time between timezones"""
        return await self.proxy.call_tool('time', 'convert_time', kwargs)
