#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="${DUMMIE_ROOT:-/media/datasets/DUMMIE Engine}"

export DUMMIE_ROOT="$ROOT_DIR"
export DUMMIE_ROOT_DIR="$ROOT_DIR"
export DUMMIE_AIWG_DIR="${DUMMIE_AIWG_DIR:-$ROOT_DIR/.aiwg}"
export DUMMIE_KUZU_DB_PATH="${DUMMIE_KUZU_DB_PATH:-$DUMMIE_AIWG_DIR/memory/loci.db}"
export DUMMIE_MCP_CONFIG_PATH="${DUMMIE_MCP_CONFIG_PATH:-$ROOT_DIR/dummie_gateway_config.json}"
export DUMMIE_N8N_ENV_FILE="${DUMMIE_N8N_ENV_FILE:-$HOME/Escritorio/n8n/.env}"
export DUMMIE_MCP_TRANSPORT="${DUMMIE_MCP_TRANSPORT:-streamable-http}"
export DUMMIE_MCP_HOST="${DUMMIE_MCP_HOST:-127.0.0.1}"
export DUMMIE_MCP_PORT="${DUMMIE_MCP_PORT:-8765}"
export DUMMIE_MCP_HTTP_PATH="${DUMMIE_MCP_HTTP_PATH:-/mcp}"

exec "$ROOT_DIR/scripts/mcp_wrapper.sh" uv run python -B layers/l1_nervous/mcp_server.py
