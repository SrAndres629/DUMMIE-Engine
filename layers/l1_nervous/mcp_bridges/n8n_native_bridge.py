#!/usr/bin/env python3
"""
n8n_native_bridge.py — MCP stdio → HTTP bridge for n8n's native MCP server.

Reads JSON-RPC from stdin, POSTs to n8n's HTTP MCP endpoint, parses SSE
response, writes JSON-RPC back to stdout.

Environment variables:
  N8N_MCP_URL   — n8n MCP HTTP endpoint (default: http://127.0.0.1:5678/mcp-server/http)
  N8N_MCP_TOKEN — JWT access token for MCP server
"""

import json
import logging
import os
import sys

import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [n8n-native-bridge] %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("n8n-native-bridge")

MCP_URL = os.environ.get("N8N_MCP_URL", "http://127.0.0.1:5678/mcp-server/http")
MCP_TOKEN = os.environ.get("N8N_MCP_TOKEN", "")

if not MCP_TOKEN:
    logger.error("N8N_MCP_TOKEN is required")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "Authorization": f"Bearer {MCP_TOKEN}",
}


def _parse_sse_response(raw: str) -> dict:
    """Parse SSE event data from n8n HTTP response.

    Format:
        event: message
        data: {"jsonrpc":"2.0","result":{...},"id":1}

    Returns the parsed JSON dict.
    """
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            return json.loads(line[len("data:") :].strip())
    # Fallback: try parsing as raw JSON (some responses may not be SSE-wrapped)
    return json.loads(raw)


def _send_request(message: dict) -> dict:
    """POST a JSON-RPC message to n8n's HTTP MCP endpoint."""
    body = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(MCP_URL, data=body, headers=HEADERS, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error("HTTP %s: %s", e.code, error_body[:500])
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": e.code,
                "message": f"HTTP {e.code}: {e.reason}",
                "data": error_body[:500],
            },
            "id": message.get("id"),
        }
    except Exception as e:
        logger.error("Request failed: %s", e)
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": message.get("id"),
        }

    return _parse_sse_response(raw)


def _write_response(response: dict):
    """Write a JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def main():
    logger.info("n8n native MCP bridge started — endpoint: %s", MCP_URL)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON: %s", e)
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                    "id": None,
                }
            )
            continue

        logger.debug(
            "stdin → %s (id=%s)", message.get("method", "?"), message.get("id")
        )
        response = _send_request(message)
        logger.debug("stdout ← id=%s", response.get("id"))
        _write_response(response)


if __name__ == "__main__":
    main()
