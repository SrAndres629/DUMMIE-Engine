#!/bin/bash
# DUMMIE Engine - SSH Sandbox Wrapper (Flat L1)
# Proxy for MCP SSH Server integration
exec npx -y @modelcontextprotocol/server-ssh "$@"
