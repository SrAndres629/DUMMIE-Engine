import json, sys, asyncio
from meta_router import MetaRouter


class MetaGateway:
    def __init__(self):
        self.router = MetaRouter()

    async def route_request(self, query: str):
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

    async def call_tool(self, query: str, tool: str, arguments: dict = None):
        import httpx

        route = await self.router.route(query)
        if not route["match"]:
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
