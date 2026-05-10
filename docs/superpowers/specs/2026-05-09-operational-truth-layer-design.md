# Operational Truth Layer Design

> Date: 2026-05-09  
> Status: Proposed  
> Scope: First snowball repair cycle for DUMMIE Engine

## Intent

DUMMIE Engine already has partial implementations for model routing, swarm coordination, action graphs, reward/penalty reputation, supervision, memory, and daemon sagas. The next repair cycle must not rebuild those pieces. It must make them measurable, connected, and useful as foundations for the next repairs.

The Operational Truth Layer is the "A before B before C" layer. It gives DUMMIE a single evidence-backed answer to:

- What is implemented?
- What is importable?
- What is tested?
- What is running now?
- What is callable through MCP?
- What is persisted?
- What is degraded, blocked, or aspirational?

Every later repair uses this truth report to pick the next easiest high-leverage fix.

## Existing Assets To Reuse

The current repo already contains the following relevant assets:

- `layers/l2_brain/model_router.py`: tier selection, fallback, token budget gate.
- `layers/l2_brain/model_discovery.py`: Ollama, Groq, and OpenRouter discovery scaffold.
- `layers/l2_brain/model_executor.py`: execution wrapper and token accounting integration.
- `layers/l2_brain/token_ledger.py`: token usage recording.
- `layers/l2_brain/neuron_ledger.py`: model reputation, rewards, penalties.
- `layers/l2_brain/action_graph.py`: action recording to 4D-TES/Kuzu.
- `layers/l2_brain/supervisor_protocol.py`: higher-tier review scaffold.
- `layers/l1_nervous/tools_impl/swarm.py`: broadcast, observe, delegate, spawn tools.
- `layers/l2_brain/daemon_diagnostic.py`: daemon inspection surface.
- `scripts/dummie_mcp_doctor.py`, `scripts/full_industrial_audit.sh`, `scripts/verify_swarm_intelligence.py`: existing diagnostic scripts.
- `.aiwg/events/file_events.jsonl`, `.aiwg/memory/*.jsonl`, `ledger/sovereign_resolutions.jsonl`: existing ledgers.

These become probes and dependencies, not things to duplicate.

## Core Principle

Do not advance to "advanced autonomous reasoning" until DUMMIE can prove the simpler substrate is alive.

The snowball order is:

1. Operational truth.
2. Contract repair.
3. Unified causal ledger.
4. Router and neuron reputation integration.
5. Minimal stable cognitive loop.
6. Controlled self-evolution.

Each phase must leave behind tests, reports, and ledger events that make the next phase easier.

## Architecture

### L2 Truth Model

Create a small L2 module that owns truth vocabulary:

- `TruthStatus`: `PASS`, `DEGRADED`, `BLOCKED`, `UNKNOWN`.
- `TruthCheck`: name, layer, status, evidence, command, error, next_repair.
- `TruthReport`: timestamp, repo_root, runtime_context, checks, summary counts.

This module must be pure Python and deterministic. It should not start daemons, mutate files, install packages, or call cloud models.

### L2 Collectors

Collectors are small functions that produce `TruthCheck` values:

- Runtime collector: detects live processes for `mcp_server.py`, `dummied`, NATS, Ollama, L6 dev server.
- Import collector: verifies key modules import cleanly.
- Model collector: calls existing `ModelDiscoveryService` and summarizes available tiers.
- Ledger collector: verifies JSONL paths exist and are append-readable/writable where safe.
- Kuzu collector: verifies `KuzuRepository` opens in native mode without lock.
- Contract collector: optionally runs a narrow smoke test list, not the full suite by default.
- MCP collector: inspects registered local tools and configured remote servers.

Collectors should degrade gracefully. A failed probe is evidence, not a crash.

### L1 MCP Surface

Expose one local MCP capability:

`local.operational_truth_report(format: "text|json" = "text", include_slow: bool = false)`

This returns the same report as the CLI. In text mode it should be concise and operator-readable. In JSON mode it should be stable enough for later UI and graph ingestion.

### CLI And Make Target

Add:

- `scripts/dummie_truth.py`
- `make verify-truth`

The CLI writes the latest machine-readable report to:

`.aiwg/reports/operational_truth.json`

The make target prints the text report and exits non-zero only for foundational blockers:

- L1 gateway code cannot import.
- L2 truth module cannot import.
- Kuzu cannot initialize at all.
- No model tier is available after defaults.

Normal degraded subsystems should be reported but should not break the command during the first phase.

## Truth Classification

Use these statuses consistently:

- `PASS`: verified by direct runtime, import, command, or tool evidence.
- `DEGRADED`: usable but not complete, not connected, missing optional provider, or operating in fallback.
- `BLOCKED`: required contract fails or path cannot execute safely.
- `UNKNOWN`: not measured yet.

Avoid "works" without evidence. Every `PASS` must name the probe.

## Handling Model Reasoning Logs

DUMMIE should not store private chain-of-thought verbatim. The persistent record should store operational traces:

- task intent
- model/agent identity
- input summary
- plan summary
- tools called
- files touched
- evidence cited
- output summary
- reviewer decision
- reward or penalty
- next repair recommendation

This preserves auditability and learning without relying on hidden reasoning text.

## Snowball Repair Phases

### Phase A: Operational Truth

Goal: DUMMIE can say what is real now.

Outputs:

- Truth data model.
- Truth collectors.
- MCP report tool.
- CLI report.
- `make verify-truth`.

This phase directly measures router, swarm, rewards, action graph, supervisor, memory, L0, L3, L5, and L6.

### Phase B: Contract Repair

Goal: fix the measured blockers that prevent a minimal saga from running.

Likely first repairs from current evidence:

- `TopologicalAuditor` does not detect `<edge source target>` cycles.
- `DummieDaemon` references `_run_cognitive_preflight`, which is missing.
- Tests still expect `_FallbackUnsafeAuditor` while runtime moved fallback behavior.
- `ModelRouter()` defaults to an empty registry in some paths instead of discovered/default models.
- `MCPDriver` can be instantiated with `mcp_gateway=None` from the orchestrator path.

### Phase C: Unified Causal Ledger

Goal: connect existing ledgers into one schema.

Do not delete existing ledgers. Add adapters so swarm events, model invocations, action graph events, token usage, and rewards can be read as one causal event stream.

### Phase D: Router Social Integration

Goal: make `NeuronLedger` influence `ModelRouter`.

The router should rank available models by capability, cost, and reputation. Rewards and penalties become inputs to future routing, not just logs.

### Phase E: Minimal Cognitive Loop

Goal: one stable loop:

`intake -> route -> execute -> verify -> supervise -> reward -> persist -> next_repair`

This is the first point where DUMMIE begins to feel like a coherent local entity instead of a collection of tools.

### Phase F: Controlled Self-Evolution

Goal: DUMMIE proposes and applies low-risk self-repairs under guardrails.

Initial mode:

- plan-only for medium/high risk
- auto-apply only for bounded low-risk repairs
- tests required
- ledger event required
- supervisor review required

## Non-Goals For Phase A

- No new UI.
- No full L0 daemon integration.
- No automatic patch application.
- No cloud-only dependency.
- No replacement of existing router/swarm/reward modules.
- No broad refactor of package layout.

## Success Criteria

Phase A is done when:

- `make verify-truth` runs locally.
- `scripts/dummie_truth.py --json` writes `.aiwg/reports/operational_truth.json`.
- MCP exposes `operational_truth_report`.
- The report identifies at least: L1 gateway, L2 Kuzu, model discovery, router registry, swarm ledger, neuron ledger, action graph, L0 daemon runtime, L3 auditors, L5 driver, and L6 surface.
- The report marks known gaps as `DEGRADED` or `BLOCKED` with next repair recommendations.

Once Phase A exists, every following repair starts by reading the truth report and ends by improving it.
