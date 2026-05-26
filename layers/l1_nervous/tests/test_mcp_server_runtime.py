from dataclasses import replace

import pytest

from layers.l1_nervous.mcp_server_runtime import (
    MCPRuntimeConfig,
    load_runtime_config,
    run_gateway,
)


def test_load_runtime_config_defaults_to_stdio_loopback():
    cfg = load_runtime_config({})

    assert cfg == MCPRuntimeConfig(
        transport="stdio",
        host="127.0.0.1",
        port=8000,
        mount_path="/",
        streamable_http_path="/mcp",
    )


def test_load_runtime_config_reads_streamable_http_overrides():
    cfg = load_runtime_config(
        {
            "DUMMIE_MCP_TRANSPORT": "streamable-http",
            "DUMMIE_MCP_HOST": "127.0.0.1",
            "DUMMIE_MCP_PORT": "8765",
            "DUMMIE_MCP_MOUNT_PATH": "/events",
            "DUMMIE_MCP_HTTP_PATH": "/gateway",
        }
    )

    assert cfg == MCPRuntimeConfig(
        transport="streamable-http",
        host="127.0.0.1",
        port=8765,
        mount_path="/events",
        streamable_http_path="/gateway",
    )


def test_run_gateway_uses_sse_mount_path_only_when_needed():
    calls = []

    class FakeMCP:
        def run(self, transport, mount_path=None):
            calls.append((transport, mount_path))

    run_gateway(FakeMCP(), MCPRuntimeConfig(transport="stdio"))
    run_gateway(FakeMCP(), replace(MCPRuntimeConfig(), transport="streamable-http"))
    run_gateway(
        FakeMCP(), replace(MCPRuntimeConfig(), transport="sse", mount_path="/events")
    )

    assert calls == [
        ("stdio", None),
        ("streamable-http", None),
        ("sse", "/events"),
    ]


def test_load_runtime_config_rejects_unknown_transport():
    with pytest.raises(ValueError, match="Unknown MCP transport"):
        load_runtime_config({"DUMMIE_MCP_TRANSPORT": "http2"})
