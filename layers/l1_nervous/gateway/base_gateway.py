import json, os, sys, asyncio
from pathlib import Path
from mcp import StdioClient, StdioServerParameters

DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine"))
AIWG_RUNTIME = DUMMIE_ROOT / ".aiwg" / "runtime" / "gateways"
BIBLIOTECA_MCP = "/home/jorand/Escritorio/Biblioteca MCP"


def _expand_env(s: str) -> str:
    for k, v in os.environ.items():
        s = s.replace(f"${{{k}}}", v)
    return s.replace("${BIBLIOTECA_MCP}", BIBLIOTECA_MCP)


class BaseGateway:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
        self.name = self.config["gateway_name"]
        self.port = self.config["port"]
        self.servers: dict[str, StdioClient] = {}
        self.readiness_path = AIWG_RUNTIME / f"{self.name}.ready"
        AIWG_RUNTIME.mkdir(parents=True, exist_ok=True)

    async def start(self):
        for name, cfg in self.config["mcp_servers"].items():
            try:
                cmd = _expand_env(cfg["command"])
                args = [_expand_env(a) for a in cfg.get("args", [])]
                env = {k: _expand_env(v) for k, v in cfg.get("env", {}).items()}
                params = StdioServerParameters(
                    command=cmd, args=args, env=env if env else None
                )
                client = StdioClient(params)
                await client.initialize()
                self.servers[name] = client
            except Exception as e:
                print(f"[{self.name}] Failed to start {name}: {e}", file=sys.stderr)
        self._write_readiness("ready")
        return self

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict = None):
        client = self.servers.get(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' not in gateway '{self.name}'")
        return await client.call_tool(tool_name, arguments or {})

    def get_capabilities(self) -> list[dict]:
        caps = []
        for srv_name in self.config["mcp_servers"]:
            client = self.servers.get(srv_name)
            if client:
                caps.append(
                    {"server": srv_name, "gateway": self.name, "port": self.port}
                )
        return caps

    async def stop(self):
        for name, client in self.servers.items():
            try:
                await client.close()
            except Exception:
                pass
        self._write_readiness("stopped")

    def _write_readiness(self, state: str):
        self.readiness_path.write_text(state)
