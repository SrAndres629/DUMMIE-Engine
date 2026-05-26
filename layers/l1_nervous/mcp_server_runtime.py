from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class MCPRuntimeConfig:
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    mount_path: str = "/"
    streamable_http_path: str = "/mcp"


def load_runtime_config(env: Mapping[str, str] | None = None) -> MCPRuntimeConfig:
    source = os.environ if env is None else env
    transport = source.get("DUMMIE_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise ValueError(f"Unknown MCP transport: {transport}")

    return MCPRuntimeConfig(
        transport=transport,
        host=source.get("DUMMIE_MCP_HOST", "127.0.0.1"),
        port=int(source.get("DUMMIE_MCP_PORT", "8000")),
        mount_path=source.get("DUMMIE_MCP_MOUNT_PATH", "/"),
        streamable_http_path=source.get("DUMMIE_MCP_HTTP_PATH", "/mcp"),
    )


def run_gateway(server, config: MCPRuntimeConfig) -> None:
    mount_path = config.mount_path if config.transport == "sse" else None
    server.run(transport=config.transport, mount_path=mount_path)
