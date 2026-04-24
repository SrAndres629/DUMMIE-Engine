---
spec_id: "DE-ADR-0016"
title: "Industrial Gear Integration (Modular Software Fabrication)"
status: "PROPOSED"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
tags: ["adr", "industrial_gears", "modular_architecture"]
---

# ADR-0016: Industrial Gear Integration (Modular Software Fabrication)

## Status
**PROPOSED**

## Context
DUMMIE Engine operates as an Autonomous Software Factory (ASF). To scale development without building every tactical tool from scratch, we identify 18 "Industrial Gears" (repositories and tools) that fulfill specific roles across the 7-layer architecture. 

However, local hardware constraints (16GB RAM) require a strategy that prevents system degradation while maximizing the injection of specialized logic.

## Decision
We will adopt an **On-Demand Sidecar Pattern** for tool integration:

1.  **MCP as the Standard Interface:** All tools that provide cognitive or data services (Mem0, Tree-sitter, etc.) will be exposed via the **Model Context Protocol (MCP)**.
2.  **Tactical Invocation:** Heavy tools (Aider, Plandex, Cline) will not be resident. They will be launched as "Ephemeral Fabrication Processes" by the **Logic Engineer** (`sw.plant.logic`).
3.  **Hardware Circuit Breaker:** The **E-Shield** (L3) will monitor RAM usage before launching a gear. If available RAM is < 2GB, heavy gear invocation will be queued or delegated to cloud endpoints (e.g., Cloud E2B).
4.  **Gear Registry:** A centralized `shared/gear_registry.json` will serve as the "Bill of Materials" (BOM) for the factory.

## Layer Mapping (The 18 Gears)

| Tool | Layer | Integration Pattern |
| :--- | :--- | :--- |
| **OpenClaw/holaOS** | L1 | Strategic Reference (Benchmarking) |
| **Plandex/Aider/Cline** | L5 | Ephemeral CLI (Muscle) |
| **Spec Kit** | L4 | SDD Enforcement Logic |
| **Cube/E2B/Daytona** | L3 | Secure Sandbox Sidecar |
| **Outlines/Guidance** | L2 | Restricted Decoding Adapter |
| **SWE-agent/OpenHands** | L2 | Verification-in-the-Loop |
| **LangGraph/Mem0** | L2 | Cognition & Memory Engine |
| **Tree-sitter** | L4 | LST Parser (Binary) |
| **Code Bundler Pro** | L4 | Context Logistics |
| **MCP Servers** | L1 | Connectivity Backbone |

## Consequences
- **Positive:** Rapid capability expansion, reduced technical debt, standardized tool interface.
- **Negative:** Increased orchestration complexity, dependency on external maintenance of gears.
- **Risk:** Hardware contention if multiple heavy gears are invoked simultaneously.

## [MSA] Sibling Components Requeridos
- **Executable Contract:** `0016-industrial-gear-integration.feature`
- **Machine Rules:** `0016-industrial-gear-integration.rules.json`
