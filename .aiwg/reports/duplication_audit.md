# Duplication Audit — DUMMIE Engine

**Generated:** 2026-05-09T03:29:00Z  
**Purpose:** Evidence-based inventory of all duplications, overlaps, and fragmentation discovered during the canonical registry creation. No files were moved or deleted.

## Executive Summary

| Duplication Type | Count | Severity |
|:---|---:|:---|
| Identity/personality sources | 5 files | 🔴 CRITICAL |
| Documentation directories | 2 directories | 🟡 HIGH |
| Skill directories | 4 directories | 🟡 HIGH |
| Spec number collisions | 11 prefixes | 🟠 MEDIUM |
| Root config files in wrong location | 4 files | 🟠 MEDIUM |
| Log files at root | 7 files | 🟢 LOW |
| Scratch/test files at root | 4 files | 🟢 LOW |
| .worktrees duplicated content | 3 worktrees | 🟡 HIGH |

---

## 1. Identity/Personality Fragmentation (CRITICAL)

Five separate files define overlapping aspects of the agent's identity:

| File | Size | Purpose | Conflicts With |
|:---|---:|:---|:---|
| `AGENTS.md` | 11.4KB | Workspace rules, memory, heartbeat, engineering mandate | GEMINI.md, MAD_COORDINATION_PROTOCOL.md |
| `GEMINI.md` | 668B | 5 collaboration roles | AGENTS.md |
| `IDENTITY.md` | 351B | Name, creature, vibe | SOUL.md, .aiwg/identity.json |
| `SOUL.md` | 1.8KB | Personality narrative | IDENTITY.md, .aiwg/identity.json |
| `.aiwg/identity.json` | 1.4KB | Machine-readable personality traits | IDENTITY.md, SOUL.md |

**Impact:** Every agent session loads ~3,760 tokens of overlapping/contradictory identity context. A local 7B model with 4K context wastes ~94% of its budget just on identity before it can work.

**Recommendation:** Merge into 2 files:
1. `.agents/prompts/sys_identity.md` — unified human-readable system prompt
2. `.aiwg/identity.json` — machine-readable personality traits (keep, it's already well-structured)

---

## 2. Documentation Directory Split (HIGH)

Two top-level documentation directories exist:

| Directory | Contents | File Count |
|:---|:---|---:|
| `doc/` | specs (52 triples), adr, guides, manifesto, agentic, deprecated | ~180+ files |
| `docs/` | ops, superpowers/plans, superpowers/specs | ~11 files |

**Impact:** Agents searching for documentation must search both directories. Cross-references may point to either. The `doc/` directory has 16x more content.

**Recommendation:** After registry stabilizes, alias `docs/` content into `doc/` or vice versa. Not urgent but must happen before adding more docs.

---

## 3. Skill Directory Fragmentation (HIGH)

Four separate directories contain skills:

| Directory | Canonical Skills | Status |
|:---|---:|:---|
| `.agents/skills/` | 27 canonical + 92 deprecated | ✅ Primary canonical location |
| `.gemini/skills/mcp_optimizer/` | 1 | ⚠️ Duplicate of mcp_gateway |
| `skills/chatgpt/` | 7 files (external pack) | ⚠️ External, not in registry |
| `skills/diagnostic/` | 1 skill | ⚠️ Not under .agents/ |
| `shared/skills/` | 0 (empty) | ❓ Ambiguous purpose |

**Impact:** An agent searching for "the diagnostic skill" might find it in `skills/diagnostic/` or fail to find it in `.agents/skills/`. An agent using MCP optimization might use the `.gemini/` version or the `.agents/` version, potentially getting different behavior.

**Recommendation:** Establish `.agents/skills/` as the single canonical location. Create symlinks or import aliases from other directories. Do NOT delete until all references are mapped.

---

## 4. Spec Number Prefix Collisions (MEDIUM)

The following spec number prefixes are used by 2+ different specs:

| Prefix | Specs |
|:---|:---|
| 11 | `arrow_data_plane`, `monorepo_structure` |
| 16 | `hardware_ipc_stability`, `mcp_dynamic_gateway` |
| 26 | `command_canvas_gui`, `langgraph_quantum_swarm` |
| 27 | `floating_session_state`, `kaizen_loop_refinement` |
| 28 | `shadow_worktrees`, `skill_standard_yaml` |
| 29 | `design_station_workflow`, `skill_ingestion_engine` |
| 30 | `floating_sessions`, `visualizer_microservice` |
| 40 | `metacognitive_audit_loop`, `self_healing_remediation_loop`, `token_optimization_protocol` |
| 41 | `layer_handshake_protocol`, `semantic_fabric_indexer`, `wordline_sovereignty` |
| 42 | `metacognitive_identity`, `ontological_certainty_map`, `proactive_heartbeat_protocol` |
| 44 | `local_reasoning_gateway`, `pervasive_channel_adapters` |

**Impact:** If any code references specs by number prefix (e.g., "apply spec 40"), it's ambiguous. Agent-generated spec references may resolve to the wrong spec.

---

## 5. Root Directory Clutter (MEDIUM)

50 files at root. Ideally root should have <15. Files that belong elsewhere:

| File | Size | Should Be |
|:---|---:|:---|
| `dummie_gateway_config.json` | 5.7KB | `.aiwg/config/` |
| `dummie_agent_config.json` | 764B | `.aiwg/config/` |
| `audit_raw.log` | 5.8KB | `.aiwg/logs/` |
| `audit_report.json` | 4.2KB | `.aiwg/reports/` |
| `debug_causal.txt` | 294B | `.aiwg/logs/` |
| `gateway_sovereign.log` | 648B | `.aiwg/logs/` |
| `l0.log` | 695B | `.aiwg/logs/` |
| `l0_monitor.log` | 1.5KB | `.aiwg/logs/` |
| `l1.log` | 257KB | `.aiwg/logs/` |
| `mcp.log` | 579B | `.aiwg/logs/` |
| `mcp_server.log` | 432B | `.aiwg/logs/` |
| `memory.log` | 2.8KB | `.aiwg/logs/` |
| `memory_sovereign.log` | 554B | `.aiwg/logs/` |
| `monitor.log` | 114B | `.aiwg/logs/` |
| `scratch_test_mcp.py` | 1.3KB | delete or `.aiwg/scratch/` |
| `test_flight.py` | 1.2KB | `tests/` |
| `test_ipc.py` | 382B | `tests/` |
| `test_spawn.py` | 770B | `tests/` |
| `verify_spec30_fix.py` | 2.7KB | `tests/` or delete |

---

## 6. .worktrees Duplication (HIGH)

Three worktrees exist with full copies of the repo:

```
.worktrees/
  agent-office-runtime/    (full repo copy)
  feature-adapters-refactor/ (full repo copy)
  feature-sdk-core/        (full repo copy)
```

Each contains copies of `proto/`, `layers/`, `scratch/`, `scripts/`, `doc/`. This inflates all file counts and can cause confusion if agents index these directories.

**Impact:** Any file search (`find`, `grep`) that doesn't explicitly exclude `.worktrees/` will return triplicate results.

**Recommendation:** Ensure `.agentignore` / `.geminiignore` exclude `.worktrees/`. Verify these worktrees are still actively used; if not, consider pruning.

---

## 7. Validator Results

```
$ python3 scripts/validate_specs_docs.py
DOC/SPEC VALIDATION FAILED
- doc/specs/49_typed_sdk_generation.md: Physical Evidence path does not exist `scratch/generate_sdks.py`
```

The spec `49_typed_sdk_generation` references a scratch script that no longer exists at the expected path (it was moved to `doc/.deprecated/scratchpad/generate_sdks.py`).

---

## High-Risk Moves Deferred

The following moves/merges were identified but **NOT executed** per instructions:

1. ❌ Merge `doc/` + `docs/` → blocked until all spec references are mapped
2. ❌ Move identity files to `.agents/core_context/` → blocked until unified prompt is created
3. ❌ Consolidate skill directories → blocked until import paths are verified
4. ❌ Move root configs to `.aiwg/config/` → blocked until startup scripts are updated
5. ❌ Move root logs to `.aiwg/logs/` → blocked until logging config is centralized
6. ❌ Fix spec 49 broken reference → requires confirming canonical path first
