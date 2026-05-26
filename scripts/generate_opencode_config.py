#!/usr/bin/env python3
"""Genera opencode.jsonc desde los SSOTs de DUMMIE Engine.
Lee models_config.json, dummie_gateway_config.json, meta_router_assignments.json
y produce la configuración completa para opencode con plugin nativo.
"""

import json
import os
import sys
from pathlib import Path

DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine"))
CONFIGS = DUMMIE_ROOT / "layers/l1_nervous/configs"
GATEWAY_CONFIG = DUMMIE_ROOT / "dummie_gateway_config.json"
MODELS_CONFIG = CONFIGS / "models_config.json"
ROUTER_ASSIGNMENTS = CONFIGS / "meta_router_assignments.json"
OUTPUT = DUMMIE_ROOT / "opencode.jsonc"


def load_json(path):
    if not path.exists():
        print(f"WARN: {path} not found", file=sys.stderr)
        return {}
    with open(path) as f:
        return json.load(f)


def generate_mcp_servers(gateway_cfg):
    servers = {}

    if "mcpServers" in gateway_cfg:
        for name, srv in gateway_cfg["mcpServers"].items():
            cmd = srv.get("command", "")
            args = srv.get("args", [])
            env = srv.get("env", {})
            servers[name] = {
                "type": "local",
                "command": [cmd] + args,
                "environment": env,
                "enabled": srv.get("enabled", True),
                "timeout": 120000,
            }

    servers["dummie-brain"] = {
        "type": "local",
        "command": [
            "/bin/bash",
            str(DUMMIE_ROOT / "scripts/mcp_wrapper.sh"),
            "uv",
            "run",
            "python",
            "-B",
            "layers/l1_nervous/mcp_server.py",
        ],
        "environment": {
            "DUMMIE_ROOT": str(DUMMIE_ROOT),
            "DUMMIE_ROOT_DIR": str(DUMMIE_ROOT),
            "DUMMIE_AIWG_DIR": str(DUMMIE_ROOT / ".aiwg"),
            "DUMMIE_KUZU_DB_PATH": str(DUMMIE_ROOT / ".aiwg/memory/loci.db"),
            "DUMMIE_MCP_CONFIG_PATH": str(DUMMIE_ROOT / "dummie_gateway_config.json"),
        },
        "enabled": True,
        "timeout": 120000,
    }

    return servers


def generate_plugin_config(models_cfg):
    default_llm = "gemma4:e2b"
    default_embedding = "qwen3-embedding"

    if models_cfg:
        defaults = models_cfg.get("defaults", {})
        default_llm = defaults.get("llm", default_llm)
        default_embedding = defaults.get("embedding", default_embedding)

    return [
        [
            str(DUMMIE_ROOT / "layers/l1_nervous/plugins/opencode-dummie"),
            {
                "dummie_root": str(DUMMIE_ROOT),
                "default_llm": default_llm,
                "default_embedding": default_embedding,
                "meta_gateway_pipeline": True,
                "sdd_guardrails": True,
                "swarm_coordination": True,
            },
        ]
    ]


def generate():
    gateway_cfg = load_json(GATEWAY_CONFIG)
    models_cfg = load_json(MODELS_CONFIG)
    router_cfg = load_json(ROUTER_ASSIGNMENTS)

    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": "opencode/deepseek-v4-flash-free",
        "small_model": "opencode/deepseek-v4-flash-free",
        "mcp": generate_mcp_servers(gateway_cfg),
        "plugin": generate_plugin_config(models_cfg),
        "permission": "allow",
        "compaction": {
            "auto": True,
            "tail_turns": 15,
        },
    }

    if router_cfg:
        config["dummie_meta_router"] = router_cfg

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    json_str = json.dumps(config, indent=2, ensure_ascii=False)
    with open(OUTPUT, "w") as f:
        f.write(json_str)
        f.write("\n")

    print(f"Generated: {OUTPUT}")
    print(f"  MCP servers: {len(config['mcp'])}")
    print(f"  Plugins: {len(config['plugin'])}")
    return config


if __name__ == "__main__":
    generate()
