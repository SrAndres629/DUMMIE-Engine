from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para puppeteer
# NO EDITAR DIRECTAMENTE.

class PuppeteerClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def puppeteer_navigate(self, **kwargs) -> Any:
        """Navigate to a URL"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_navigate', kwargs)

    async def puppeteer_screenshot(self, **kwargs) -> Any:
        """Take a screenshot of the current page or a specific element"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_screenshot', kwargs)

    async def puppeteer_click(self, **kwargs) -> Any:
        """Click an element on the page"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_click', kwargs)

    async def puppeteer_fill(self, **kwargs) -> Any:
        """Fill out an input field"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_fill', kwargs)

    async def puppeteer_select(self, **kwargs) -> Any:
        """Select an element on the page with Select tag"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_select', kwargs)

    async def puppeteer_hover(self, **kwargs) -> Any:
        """Hover an element on the page"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_hover', kwargs)

    async def puppeteer_evaluate(self, **kwargs) -> Any:
        """Execute JavaScript in the browser console"""
        return await self.proxy.call_tool('puppeteer', 'puppeteer_evaluate', kwargs)
