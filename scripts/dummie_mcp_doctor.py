#!/usr/bin/env python3
"""Operational checks for the DUMMIE Brain MCP gateway.

This script validates the effective Codex CLI registration, performs a real MCP
stdio handshake, and reports process/config drift without killing anything.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / "layers" / "l2_brain" / ".venv" / "bin" / "python"
SERVER = ROOT / "layers" / "l1_nervous" / "mcp_server.py"
GATEWAY_CONFIG = ROOT / "dummie_gateway_config.json"
CANONICAL_DB = ROOT / ".aiwg" / "memory" / "loci.db"
SOCKET = ROOT / ".aiwg" / "sockets" / "flight.sock"
DUMMIED_SOCKET = ROOT / ".aiwg" / "sockets" / "dummied.sock"


def gateway_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "DUMMIE_ROOT_DIR": str(ROOT),
            "DUMMIE_AIWG_DIR": str(ROOT / ".aiwg"),
            "DUMMIE_KUZU_DB_PATH": str(CANONICAL_DB),
            "DUMMIE_DUMMIED_SOCKET_PATH": str(DUMMIED_SOCKET),
            "DUMMIE_MCP_CONFIG_PATH": str(GATEWAY_CONFIG),
            "MEMORY_SOCKET_PATH": str(SOCKET),
            "PYTHONPATH": ":".join(
                [
                    str(ROOT / "layers" / "l2_brain"),
                    str(ROOT / "layers" / "l1_nervous"),
                    str(ROOT / "layers" / "l3_shield"),
                ]
            ),
        }
    )
    return env


def run_command(args: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=20)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "timeout"
    return proc.returncode, proc.stdout, proc.stderr


def check_codex_config() -> bool:
    code, stdout, stderr = run_command(["codex", "mcp", "get", "dummie-brain", "--json"])
    if code != 0:
        print(f"codex_config=FAIL code={code} stderr={stderr.strip()}")
        return False

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        print(f"codex_config=FAIL invalid_json={exc}")
        return False

    transport = data.get("transport", {})
    ok = (
        data.get("enabled") is True
        and transport.get("type") == "stdio"
        and Path(transport.get("command", "")) == PYTHON
        and transport.get("args") == [str(SERVER)]
        and transport.get("env", {}).get("DUMMIE_KUZU_DB_PATH") == str(CANONICAL_DB)
    )
    print(f"codex_config={'OK' if ok else 'FAIL'} name={data.get('name')} enabled={data.get('enabled')}")
    return ok


def audit_gateway_config() -> bool:
    if not GATEWAY_CONFIG.exists():
        print(f"gateway_config=FAIL missing={GATEWAY_CONFIG}")
        return False

    data = json.loads(GATEWAY_CONFIG.read_text())
    servers: dict[str, dict[str, Any]] = data.get("mcpServers", {})
    active = sorted(name for name, cfg in servers.items() if not cfg.get("disabled", False))
    disabled = sorted(name for name, cfg in servers.items() if cfg.get("disabled", False))
    external = sorted(
        name
        for name, cfg in servers.items()
        if cfg.get("command") in {"npx", "uvx"} and not cfg.get("disabled", False)
    )
    print(f"gateway_config=OK servers={len(servers)} active={len(active)} disabled={len(disabled)}")
    if external:
        print(f"gateway_external_active={','.join(external)}")
    return True


def inspect_processes() -> bool:
    code, stdout, stderr = run_command(["ps", "-eo", "pid,ppid,stat,comm,args"])
    if code != 0:
        print(f"process_scan=FAIL code={code} stderr={stderr.strip()}")
        return False

    relevant = []
    legacy = []
    for line in stdout.splitlines():
        low = line.lower()
        if "mcp_server.py" in low or "memory_server" in low or "flight.sock" in low:
            if "dummie_mcp_doctor.py" not in line:
                relevant.append(line.strip())
        if "kuzu_data" in line:
            legacy.append(line.strip())

    print(f"process_scan=OK relevant={len(relevant)} legacy_kuzu_data={len(legacy)}")
    for line in relevant[:20]:
        print(f"process: {line}")
    if len(relevant) > 20:
        print(f"process: ... truncated {len(relevant) - 20} more")
    for line in legacy[:10]:
        print(f"legacy_path: {line}")
    return not legacy


def inspect_runtime_sockets() -> bool:
    sockets = {
        "dummied_socket": DUMMIED_SOCKET,
        "legacy_aiwg_dummied_socket": ROOT / ".aiwg" / "dummied.sock",
        "legacy_tmp_dummied_socket": Path("/tmp/dummied.sock"),
        "flight_socket": SOCKET,
    }
    for label, path in sockets.items():
        state = "present" if path.exists() else "missing"
        print(f"socket:{label}={state} path={path}")
    return True


async def check_mcp_handshake(call_discovery: bool) -> bool:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(
        command=str(PYTHON),
        args=[str(SERVER)],
        env=gateway_env(),
        cwd=str(ROOT),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            resources = await session.list_resources()
            tool_names = sorted(tool.name for tool in tools.tools)
            resource_uris = sorted(str(resource.uri) for resource in resources.resources)
            print(f"mcp_handshake=OK tools={len(tool_names)} resources={len(resource_uris)}")
            print(f"mcp_tools={','.join(tool_names)}")
            print(f"mcp_resources={','.join(resource_uris)}")

            health = await session.read_resource("brain://health")
            health_text = "\n".join(getattr(item, "text", "") for item in health.contents)
            print(f"brain_health={health_text.strip()}")

            identity = await session.read_resource("brain://identity")
            identity_text = "\n".join(getattr(item, "text", "") for item in identity.contents)
            print(f"brain_identity={identity_text.strip()}")

            if call_discovery:
                result = await session.call_tool("dummie_discover_capabilities", {"query": ""})
                text = "\n".join(getattr(item, "text", "") for item in result.content)
                print("discover_default=OK")
                print(text[:2000])
    return True


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-codex",
        action="store_true",
        help="Skip effective Codex CLI registration check.",
    )
    parser.add_argument(
        "--call-discovery",
        action="store_true",
        help="Call dummie_discover_capabilities with an empty query after handshake.",
    )
    args = parser.parse_args()

    ok = True
    if not PYTHON.exists():
        print(f"python=FAIL missing={PYTHON}")
        ok = False
    if not SERVER.exists():
        print(f"server=FAIL missing={SERVER}")
        ok = False

    if ok and not args.skip_codex:
        ok = check_codex_config() and ok
    ok = audit_gateway_config() and ok
    ok = inspect_processes() and ok
    ok = inspect_runtime_sockets() and ok

    try:
        ok = await check_mcp_handshake(args.call_discovery) and ok
    except Exception as exc:
        print(f"mcp_handshake=FAIL error={exc}")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
