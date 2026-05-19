# .aiwg/strategic/ — DUMMIE Strategic Thinking & Architecture

**Purpose:** Structured strategic thinking, architecture decisions, and execution plans that DUMMIE can consume automatically for continuity and traceability.

**Rule:** Everything here is machine-readable AND human-readable. DUMMIE reads these files at session start to recall strategic context.

---

## File Index

| File | Type | Purpose | Last Updated |
|------|------|---------|-------------|
| `l2_brain_architecture_thinking.md` | MD | Strategic thinking about L2 architecture | 2026-05-19 |
| `l2_brain_execution_plan.json` | JSON | Session-based execution plan for PACK R3 | 2026-05-19 |
| `dummie_runtime_profile.yaml` | YAML | Honest assessment of DUMMIE's operational capabilities | 2026-05-19 |
| `l2_canonical_manifest.yaml` | YAML | Proposed canonical architecture for L2 Brain | 2026-05-19 |

## How DUMMIE Uses These Files

```
Session Start
    ↓
Read .aiwg/strategic/*.md, *.json, *.yaml
    ↓
Reconstruct strategic context from files
    ↓
Execute current session objectives
    ↓
Update files with session results
    ↓
Session End (memory persists in files)
```

## Active Plans

| Plan | Status | Next Session | Owner |
|------|--------|-------------|-------|
| PACK R2.1 (Flat Brain Repair) | ✅ COMPLETE | N/A | DUMMIE |
| PACK R3 (L2 Architecture) | 📋 DRAFT — awaiting Jorge approval | R3-S1 | DUMMIE + Jorge |

## Decision Log

| Date | Decision | Status | Reference |
|------|----------|--------|-----------|
| 2026-05-19 | flat_brain/ migration happened without manifest | Documented | l2_brain_architecture_thinking.md |
| 2026-05-19 | 5 files restored, 58 specs repaired | Executed | PACK R2.1 reports |
| 2026-05-19 | L2 architecture contract needed before R3 | Proposed | l2_canonical_manifest.yaml |
| 2026-05-19 | Session-based execution model defined | Proposed | l2_brain_execution_plan.json |

## Pending Decisions (Jorge's Input Required)

1. **flat_brain/ permanence** — Keep as final structure or reorganize?
2. **src/brain/ role** — Absorb into canonical or eliminate?
3. **Test location** — Inside flat_brain/ or separate?
4. **Import strategy** — Compatibility shim or full migration?
5. **Persistence policy** — KùzuDB only or KùzuDB + Redb?

## Continuity Protocol

Between sessions:
- **Daemon** runs heartbeat checks every ~30 minutes
- **Memory files** (`memory/YYYY-MM-DD.md`) log what happened
- **MEMORY.md** holds distilled long-term memory
- **This directory** holds strategic thinking and plans

At session start:
1. Read `MEMORY.md` for long-term context
2. Read recent `memory/YYYY-MM-DD.md` for recent events
3. Read `.aiwg/strategic/` for active plans and decisions
4. Resume work from last known state

## Adding New Strategic Documents

When DUMMIE has strategic thinking to preserve:
1. Create file in `.aiwg/strategic/` with appropriate extension
2. Update this README index
3. Reference in decision log
4. Use in next session for continuity
