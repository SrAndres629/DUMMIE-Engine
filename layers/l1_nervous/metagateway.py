import json
import sys
import os
import asyncio
import logging
from meta_router import MetaRouter

logger = logging.getLogger("dummie-smart.metagateway")


class MetaGateway:
    def __init__(self, use_smart=None):
        self.router = MetaRouter()

        if use_smart is None:
            use_smart = os.environ.get("DUMMIE_USE_SMART_ROUTING", "").lower() in (
                "1",
                "true",
                "yes",
            )
        self.use_smart = use_smart

        self.cache = None
        self.smart_router = None
        self.budget_router = None
        self._warmup_task = None

        if self.use_smart:
            try:
                from semantic_cache import SemanticRouteCache
                from smart_router import SmartRouter
                from context_budget_tools import ContextBudgetRouter

                self.cache = SemanticRouteCache()
                self.smart_router = SmartRouter()
                self.budget_router = ContextBudgetRouter()
                try:
                    loop = asyncio.get_running_loop()
                    self._warmup_task = loop.create_task(
                        self.smart_router.warm_kv_cache()
                    )
                except RuntimeError:
                    pass
                logger.info("SMART routing enabled (env DUMMIE_USE_SMART_ROUTING=1)")
            except Exception as e:
                logger.warning(
                    "SMART init failed, falling back to classic routing: %s", e
                )
                self.use_smart = False

    async def route_request(self, query: str, context_budget: int = 4096):
        if not self.use_smart:
            return await self._route_old(query)
        return await self._route_smart(query, context_budget)

    async def _route_old(self, query: str):
        route = await self.router.route(query)
        if not route["match"]:
            return {
                "error": True,
                "message": route.get("message", "No matching gateway"),
                "confidence": route.get("confidence", 0.0),
                "domain": route.get("domain"),
            }
        result = {
            "gateway": route["gateway"],
            "port": route["port"],
            "servers": route["servers"],
            "domain": route["domain"],
            "action": route["action"],
            "confidence": route["confidence"],
            "query": query,
        }
        if "delegation" in route:
            result["delegation"] = route["delegation"]
        return result

    async def _route_smart(self, query: str, context_budget: int):
        try:
            cached = await self.cache.get(query) if self.cache else None
            if cached:
                return cached

            tools = self.budget_router.get_tools_for_budget(context_budget)
            route = await self.smart_router.route(query, tools)

            if route.get("match") and self.cache:
                asyncio.create_task(self.cache.set(query, route))

            return route
        except Exception as e:
            logger.error("SMART routing failed, falling back: %s", e)
            return await self._route_old(query)

    async def call_tool(self, query: str, tool: str, arguments: dict = None):
        import httpx

        route = await self._route_old(query)
        if not route.get("match"):
            raise ValueError(f"No gateway found for: {query}")
        delegation = route.get("delegation", {})
        target_server = delegation.get("server", route["servers"][0])
        target_location = delegation.get("location", "local")
        if target_location == "cloud":
            raise NotImplementedError(
                f"Cloud execution not yet implemented for '{target_server}' via MetaGateway"
            )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"http://localhost:{route['port']}/call",
                json={
                    "server": target_server,
                    "tool": tool,
                    "arguments": arguments or {},
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()

    def list_capabilities(self):
        return self.router.list_all_capabilities()


if __name__ == "__main__":

    async def main():
        mg = MetaGateway()
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
                query = msg.get("query", "")
                result = await mg.route_request(query)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            except Exception as e:
                print(json.dumps({"error": True, "message": str(e)}), flush=True)

    asyncio.run(main())
