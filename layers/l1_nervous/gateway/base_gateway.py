import json, os, sys, asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from mcp import StdioServerParameters, stdio_client, ClientSession

DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
AIWG_RUNTIME = DUMMIE_ROOT / ".aiwg" / "runtime" / "gateways"
BIBLIOTECA_MCP = os.environ.get(
    "BIBLIOTECA_MCP", "/home/jorand/Escritorio/Biblioteca MCP"
)
ALLOW_MANUAL_RUN = os.environ.get("DUMMIE_ALLOW_MANUAL_GATEWAY", "") == "1"


def _is_under_systemd() -> bool:
    try:
        with open("/proc/self/cgroup") as fh:
            return any(".service" in line for line in fh)
    except Exception:
        return False


def _enforce_systemd_allegiance():
    if not _is_under_systemd() and not ALLOW_MANUAL_RUN:
        print(
            f"[gateway] REFUSING to start outside systemd. "
            f"Use systemctl or set DUMMIE_ALLOW_MANUAL_GATEWAY=1 for dev bypass.",
            file=sys.stderr,
        )
        sys.exit(77)


def _expand_env(s: str) -> str:
    for k, v in os.environ.items():
        s = s.replace(f"${{{k}}}", v)
    return s.replace("${BIBLIOTECA_MCP}", BIBLIOTECA_MCP)


class BaseGateway:
    def __init__(self, config_path: str):
        _enforce_systemd_allegiance()
        with open(config_path) as f:
            self.config = json.load(f)
        self.name = self.config["gateway_name"]
        self.port = self.config["port"]
        self._sessions: dict[str, ClientSession] = {}
        self._contexts: list[asynccontextmanager] = []
        self.readiness_path = AIWG_RUNTIME / f"{self.name}.ready"
        AIWG_RUNTIME.mkdir(parents=True, exist_ok=True)

    @asynccontextmanager
    async def _connect_server(self, name: str, cfg: dict):
        cmd = _expand_env(cfg["command"])
        args = [_expand_env(a) for a in cfg.get("args", [])]
        env = {k: _expand_env(v) for k, v in cfg.get("env", {}).items()}
        params = StdioServerParameters(command=cmd, args=args, env=env if env else None)
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                yield session

    async def start(self):
        for name, cfg in self.config["mcp_servers"].items():
            try:
                cm = self._connect_server(name, cfg)
                session = await cm.__aenter__()
                self._sessions[name] = session
                self._contexts.append(cm)
                print(f"[{self.name}] Connected {name}", file=sys.stderr)
            except Exception as e:
                print(f"[{self.name}] Failed to start {name}: {e}", file=sys.stderr)
        self._write_readiness("ready")
        return self

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict = None):
        session = self._sessions.get(server_name)
        if not session:
            raise ValueError(f"Server '{server_name}' not in gateway '{self.name}'")
        return await session.call_tool(tool_name, arguments or {})

    def get_capabilities(self) -> list[dict]:
        caps = []
        for srv_name in self.config["mcp_servers"]:
            if srv_name in self._sessions:
                caps.append(
                    {"server": srv_name, "gateway": self.name, "port": self.port}
                )
        return caps

    async def stop(self):
        for cm in reversed(self._contexts):
            try:
                await cm.__aexit__(None, None, None)
            except Exception:
                pass
        self._sessions.clear()
        self._contexts.clear()
        self._write_readiness("stopped")

    def _write_readiness(self, state: str):
        self.readiness_path.write_text(state)
