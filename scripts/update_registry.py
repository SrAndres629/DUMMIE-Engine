#!/usr/bin/env python3
"""Update MCP Registry to v1.8.0 — adds missing MetaGateway + MCP infrastructure files."""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

REGISTRY_PATH = Path("/media/datasets/DUMMIE Engine/.aiwg/registry/mcp_registry.json")


@dataclass
class RegistryItem:
    path: str
    kind: str
    status: str = "active"
    canonical_target: Optional[str] = None
    owner_layer: str = "l1_nervous"
    risk: str = "low"
    reason: str = ""
    recommended_action: str = "keep"
    spec: Optional[int] = None

    def to_dict(self):
        d = {"path": self.path, "kind": self.kind, "status": self.status}
        if self.canonical_target:
            d["canonical_target"] = self.canonical_target
        d["owner_layer"] = self.owner_layer
        d["risk"] = self.risk
        d["reason"] = self.reason
        d["recommended_action"] = self.recommended_action
        if self.spec:
            d["spec"] = self.spec
        return d


NEW_ITEMS = [
    # ── l1_nervous core MCP infrastructure ──
    RegistryItem(
        path="layers/l1_nervous/tools.py",
        kind="mcp_tool_registration",
        owner_layer="l1_nervous",
        risk="high",
        reason="Master tool registration (276 lines). Registers 8 tool domains + 3 Meta-Gateway tools. Central dispatch.",
    ),
    RegistryItem(
        path="layers/l1_nervous/mcp_registry.py",
        kind="mcp_registry_runtime",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Runtime MCP registry for dynamic capability discovery.",
    ),
    RegistryItem(
        path="layers/l1_nervous/resources.py",
        kind="mcp_resource_manager",
        owner_layer="l1_nervous",
        risk="low",
        reason="System resources abstraction for MCP resource management.",
    ),
    RegistryItem(
        path="layers/l1_nervous/utils.py",
        kind="mcp_utility",
        owner_layer="l1_nervous",
        risk="low",
        reason="Shared utilities across l1_nervous MCP layer.",
    ),
    # ── tools_impl/ (MCP tool implementations) ──
    RegistryItem(
        path="layers/l1_nervous/tools_impl/__init__.py",
        kind="mcp_tool_impl_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for tools_impl directory.",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/core.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Core tool implementations (ping, config, health).",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/gateway.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="high",
        reason="Gateway tool implementations — dummie_discover, dummie_execute, dummie_analyze.",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/knowledge.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Knowledge tool implementations (memory, graph, vault queries).",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/local_reasoning.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Local reasoning tool implementations (LLM bridge, chain-of-thought).",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/metacognition.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Metacognitive tool implementations (self-evaluation, reflection).",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/nervous.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Nervous system tool implementations (memory IPC, state).",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/patch_transactions.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Patch transaction tool implementations for atomic code changes.",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/sdd.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="SDD (Sovereign Design Document) tool implementations.",
    ),
    RegistryItem(
        path="layers/l1_nervous/tools_impl/swarm.py",
        kind="mcp_tool_impl",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Swarm tool implementations (multi-agent coordination).",
    ),
    # ── context/ (6D Context Engine — Spec 170) ──
    RegistryItem(
        path="layers/l1_nervous/context/__init__.py",
        kind="context_engine_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for 6D Context Engine.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/context_engine.py",
        kind="context_engine",
        owner_layer="l1_nervous",
        risk="medium",
        reason="ContextEngine: orchestrates 6 dimensions into ContextProfile for enriched routing.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/cot_enricher.py",
        kind="context_cot",
        owner_layer="l1_nervous",
        risk="low",
        reason="CoTEnricher: generates chain-of-thought prompts with 6D context injection.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/obsidian_bridge.py",
        kind="context_obsidian",
        owner_layer="l1_nervous",
        risk="low",
        reason="ObsidianBridge: searches Obsidian vault for episodic context.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/socratic_bridge.py",
        kind="context_socratic",
        owner_layer="l1_nervous",
        risk="low",
        reason="SocraticBridge: generates clarifying questions for ambiguous queries.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/__init__.py",
        kind="context_dimension_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for 6D context dimension modules.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/temporal.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Temporal dimension: timestamp, session, recency analysis.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/spatial.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Spatial dimension: workspace path, project, filesystem location.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/semantic.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Semantic dimension: embedding-based query similarity.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/relational.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Relational dimension: ontology classes (DEBT, MEMORY, SAFETY, etc.).",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/episodic.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Episodic dimension: recent decisions from router log + memory.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/context/dimensions/instrumental.py",
        kind="context_dimension",
        owner_layer="l1_nervous",
        risk="low",
        reason="Instrumental dimension: available MCPs per sub-gateway.",
        spec=170,
    ),
    # ── configs/ (Sub-gateway SSOT configs — Spec 170) ──
    RegistryItem(
        path="layers/l1_nervous/configs/gateway_media.json",
        kind="ssot_gateway_config",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Media sub-gateway SSOT config. Port 8081. muapi, mcp-comfyui servers.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/configs/gateway_code.json",
        kind="ssot_gateway_config",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Code sub-gateway SSOT config. Port 8082. github, git, filesystem servers.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/configs/gateway_infra.json",
        kind="ssot_gateway_config",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Infrastructure sub-gateway SSOT config. Port 8083. docker, cloudflare servers.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/configs/gateway_knowledge.json",
        kind="ssot_gateway_config",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Knowledge sub-gateway SSOT config. Port 8084. sqlite, sequentialthinking servers.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/configs/gateway_shell.json",
        kind="ssot_gateway_config",
        owner_layer="l1_nervous",
        risk="medium",
        reason="Shell sub-gateway SSOT config. Port 8085. shell, mcp-bash, browser-use servers.",
        spec=170,
    ),
    # ── __init__ packages (Spec 170 structure) ──
    RegistryItem(
        path="layers/l1_nervous/embeddings/__init__.py",
        kind="embedding_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for embeddings module.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/gateway/__init__.py",
        kind="gateway_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for gateway module.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l1_nervous/models/__init__.py",
        kind="model_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for models module.",
        spec=171,
    ),
    RegistryItem(
        path="layers/l1_nervous/models/adapters/__init__.py",
        kind="adapter_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for model adapters module.",
        spec=171,
    ),
    RegistryItem(
        path="layers/l1_nervous/routing/__init__.py",
        kind="routing_pkg",
        owner_layer="l1_nervous",
        risk="low",
        reason="Package init for routing pipeline module.",
        spec=171,
    ),
    # ── Production scripts ──
    RegistryItem(
        path="scripts/optimize_memory.sh",
        kind="memory_optimization_script",
        owner_layer="scripts",
        risk="low",
        reason="Memory optimization: zram zstd, swap hierarchy (zram prio 100 > swapfile 1), CUDA unified memory.",
    ),
    RegistryItem(
        path="scripts/verify_metagateway.py",
        kind="verification_script",
        owner_layer="scripts",
        risk="low",
        reason="MetaGateway verification: 12 routing tests (exact match + embedding fallback).",
    ),
    RegistryItem(
        path="scripts/verify_pipeline.py",
        kind="verification_script",
        owner_layer="scripts",
        risk="low",
        reason="Routing pipeline verification: 5 strategies + Gemma 3 local LLM.",
    ),
    RegistryItem(
        path="scripts/bootstrap.sh",
        kind="bootstrap_script",
        owner_layer="scripts",
        risk="low",
        reason="System bootstrap: installs deps, initializes Kuzu DB, configures permissions.",
    ),
    RegistryItem(
        path="scripts/dummie_orchestrator.py",
        kind="orchestrator",
        owner_layer="scripts",
        risk="high",
        reason="Production orchestrator: manages MCP gateway lifecycle, daemon process.",
    ),
    RegistryItem(
        path="scripts/dummie-engine.service",
        kind="systemd_service",
        owner_layer="scripts",
        risk="medium",
        reason="Systemd service unit for DUMMIE Engine daemonization.",
    ),
    # ── l2_brain MCP infrastructure ──
    RegistryItem(
        path="layers/l2_brain/mcp_server.py",
        kind="mcp_server_l2",
        owner_layer="l2_brain",
        risk="high",
        reason="L2 Brain MCP server: serves dummie-brain tools with Kuzu DB, semantic memory, ontology.",
    ),
    RegistryItem(
        path="layers/l2_brain/metagateway_adapter.py",
        kind="metagateway_adapter",
        owner_layer="l2_brain",
        risk="medium",
        reason="Adapts MetaGateway routing decisions for L2 brain consumption.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l2_brain/metagateway_policy.py",
        kind="metagateway_policy",
        owner_layer="l2_brain",
        risk="medium",
        reason="Routing policies: local-first, cloud-first, cost-aware delegation rules.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l2_brain/metagateway_runtime_meter.py",
        kind="metagateway_meter",
        owner_layer="l2_brain",
        risk="low",
        reason="Runtime metering: latency, cost, success rate per gateway route.",
        spec=170,
    ),
    RegistryItem(
        path="layers/l2_brain/semantic_ontology_mapper.py",
        kind="semantic_ontology_mapper",
        owner_layer="l2_brain",
        risk="medium",
        reason="Intent-to-ontology mapper: maps user intent to DEBT/MEMORY/SAFETY ontology classes.",
    ),
    # ── l5_muscle execution layer ──
    RegistryItem(
        path="layers/l5_muscle/__init__.py",
        kind="muscle_pkg",
        owner_layer="l5_muscle",
        risk="low",
        reason="Package init for L5 muscle layer.",
    ),
    RegistryItem(
        path="layers/l5_muscle/compactor.py",
        kind="muscle_compactor",
        owner_layer="l5_muscle",
        risk="low",
        reason="Context compaction for efficient muscle execution.",
    ),
    RegistryItem(
        path="layers/l5_muscle/manager.py",
        kind="muscle_manager",
        owner_layer="l5_muscle",
        risk="low",
        reason="Muscle layer lifecycle manager: process pool, resource limits.",
    ),
    RegistryItem(
        path="layers/l5_muscle/workstation_operator.py",
        kind="muscle_operator",
        owner_layer="l5_muscle",
        risk="low",
        reason="Workstation operator: safely executes commands in trusted workstation mode.",
    ),
]


def load_registry(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_registry(path: Path, registry: dict):
    with open(path, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"✅ Registry saved: {path} ({len(registry['items'])} items)")


def exists(items: list[dict], path: str) -> bool:
    return any(item["path"] == path for item in items)


def build_registry_v180(existing: dict) -> dict:
    import copy

    registry = copy.deepcopy(existing)
    existing_paths = {item["path"] for item in registry["items"]}
    added = 0

    for item in NEW_ITEMS:
        if item.path in existing_paths:
            continue
        registry["items"].append(item.to_dict())
        added += 1

    # Update metadata
    registry["_meta"]["version"] = "1.8.0"
    registry["_meta"]["generated_at"] = "2026-05-22T00:00:00Z"
    registry["_meta"]["generated_by"] = "update_registry.py"
    registry["version"] = "1.8.0"
    registry["total_items"] = len(registry["items"])

    # Recalculate summary
    status_counts = {}
    for item in registry["items"]:
        st = item.get("status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    registry["summary"] = {
        "total_items": len(registry["items"]),
        "status_counts": dict(sorted(status_counts.items())),
        "architecture_notes": existing.get("summary", {}).get("architecture_notes", []),
        "critical_issues": [
            "dummie_gateway_config.json at root should be in .aiwg/config/ or .agents/config/",
            "Log files (mcp.log, mcp_server.log) should be gitignored and directed to .aiwg/logs/",
        ],
    }

    print(f"   Added: {added} new items")
    print(f"   Total: {len(registry['items'])} items")
    return registry


def main():
    registry = load_registry(REGISTRY_PATH)
    updated = build_registry_v180(registry)
    save_registry(REGISTRY_PATH, updated)


if __name__ == "__main__":
    main()
