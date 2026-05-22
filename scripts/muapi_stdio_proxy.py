#!/usr/bin/env python3
"""Stdio-to-HTTP MCP proxy for muapi-mcp-server.
Reads JSON-RPC from stdin, forwards to api.muapi.ai/mcp via HTTP, writes response to stdout.
"""

import json, os, sys, urllib.request, urllib.error

MUAPI_URL = os.environ.get("MUAPI_MCP_URL", "https://api.muapi.ai/mcp")
MUAPI_KEY = os.environ.get("MUAPI_KEY", os.environ.get("MUAPI_SANDBOX_KEY", ""))


def forward(request):
    data = json.dumps(request).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MUAPI_KEY}",
    }
    req = urllib.request.Request(MUAPI_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": e.code, "message": e.reason},
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -1, "message": str(e)},
        }


if __name__ == "__main__":
    if not MUAPI_KEY:
        print('{"jsonrpc":"2.0","error":{"code":-32000,"message":"MUAPI_KEY not set"}}')
        sys.exit(1)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = forward(request)
        print(json.dumps(response), flush=True)
