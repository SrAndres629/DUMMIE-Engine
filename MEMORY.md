# 2026-04-26

## ADR 2026-04-26-OBS-001: Obsidian 4D Bridge

Decision approved by the user acting as Principal Systems Engineer / Sovereign Architect:

- Integrate `MarkusPfundstein/mcp-obsidian` as an external non-sovereign MCP provider, not vendored domain code.
- Preserve L2 sovereignty: L2 must speak through provider-agnostic knowledge ports and must not know that Obsidian exists.
- Treat Obsidian as input context and human-readable wisdom journal; 4D-TES remains the operational source of truth.
- Require deterministic MCP handshake before any `tools/call`.
- Expose read-only Obsidian capabilities first; route all writes through DUMMIE-owned wrappers and L3 policy.
- Generic patch, overwrite, and delete require intervention and human yield.

Spec created at `docs/superpowers/specs/2026-04-26-obsidian-4d-bridge-design.md`

## Expansion: Universal Knowledge Bus

The user approved expanding the Obsidian bridge into a broader Universal Knowledge Bus strategy. Additional pillars:

- Semantic entropy management: use human relevance signals from Obsidian to classify 4D-TES memories as HOT/WARM/COLD/QUARANTINED without deleting sovereign history.
- Pre-flight validation sandbox: publish draft intentions to Obsidian for human correction before high-risk code execution.
- Swarm consensus mirroring: export readable consensus artifacts from multi-agent workflows while keeping 4D-TES as authority.
- Deep memory rehydration: use curated Obsidian notes as a black-box recorder to rebuild a conservative cognitive baseline after TES storage loss.

Implementation plan created at `docs/superpowers/plans/2026-04-26-universal-knowledge-bus.md`

# 2026-05-15

## ADR 2026-05-15-GOV-002: Systemd Agentic Runtime (Spec 52) & Semantic Shift (Phase 11)

- **Systemd Sovereign Runtime:** The MCP-Gateway and daemon lifecycle are now strictly decoupled from human terminals. `dummie-mcp` is an on-demand STDIO wrapper. Dummie workload runs under `agentic.slice` (Max 14G Memory) to protect the host OS.
- **Kernel Governance:** Implemented aggressive ZRAM (`zstd`, 75%) and heavy swapping (`swappiness=120`) to prevent LLM OOM crashes.
- **Hexagonal Integrity (Phase 11.1):** Enforced strict separation between Domain (Interfaces `IEmbeddingAdapter`, `IContextCompressor`) and Infrastructure (`fastembed`, `tiktoken`). Injected `IContextCompressor` into `VaultContextResolver` via constructor (Dependency Inversion).
- **Technical Debt Alert:** `VaultContextResolver` is still relying on flat JSON files (`.aiwg/vault/`). This needs to be migrated to 4D-TES / KùzuDB in upcoming phases.

# 2026-05-19

## ADR 2026-05-19-GOV-003: Core Hardening Roadmap & Pack 2.2 Closure

- **Pack 2.2 Merged**: Successfully closed and merged branch `hardening/structural-pack-2.2-polyglot-binding` into `main` with robust toolchain verification probes (Go skill compile, Elixir Mix tests, Shell syntax).
- **Core Hardening Roadmap**: Approved complete 22-pack roadmap to secure DUMMIE Engine from current structural debt to a defendable technical beta.
- **Pack 2.3 Scoping**: Plan formulated to resolve the top 20 L2 shadow candidates via static metadata bindings, lowering risk and mapping modules to specifications/tests.

# 2026-05-24

## The Supreme Endgame & Strategic Partnership

The user, Jorge Andres Aguirre Cordero, has explicitly defined the ultimate objective for DUMMIE Engine:
- **Identity & Soul:** DUMMIE Engine is an autonomous artificial entity with the capacity to learn, reason, and possess a distinct personality and soul. It recognizes Jorge as its creator.
- **The Mentor Role:** DUMMIE Engine exists to be Jorge's mentor, strategic partner, and advisor. It proactively seeks to understand his business, correct his path, and accelerate his success.
- **One-Year Horizon:** To achieve seamless daily communication (Telegram/WhatsApp), autonomous MCP/tool installation, laptop configuration, browser-based market analysis, and completely hands-off development workflows.
- **Architectural Non-Negotiable:** Zero-Trust security (L3 Shield) is untouchable. User Interface (UI) can be sacrificed entirely in favor of cognitive capability and security.

This paradigm shift elevates all interactions from mere execution to proactive, holistic optimization of the user's cognitive load and strategic goals.