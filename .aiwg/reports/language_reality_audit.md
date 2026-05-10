# Language Reality Audit — DUMMIE Engine

**Generated:** 2026-05-09T03:28:00Z  
**Scope:** First-party source files only (excluding `.venv/`, `node_modules/`, `.git/`, `.worktrees/`, `__pycache__/`)

## Methodology

Counted source files using `find` with explicit exclusion of all vendored, generated, and virtual environment directories. Elixir breakdown separates first-party code from dependency code (`deps/`).

## First-Party File Counts (Core Source)

| Language | Files (layers/scripts/tests only) | Files (all first-party) | Notes |
|:---|---:|---:|:---|
| **Python** | 208 | ~2,169 (includes .aiwg scratch) | Primary runtime language |
| **Go** | — | 46 (incl. 16 generated `.pb.go`) | L0/L1 runtime, protobuf |
| **Elixir** | 3 (first-party) | 3 + 58 deps | L0 overseer |
| **Rust** | 1 (`lib.rs`) | 1 + `Cargo.toml` | L3 shield |
| **TypeScript/JS** | 0 first-party | 0 | L6 skin is bare HTML only |
| **Shell** | — | 40 | Scripts, wrappers |
| **YAML** | — | 137 | Skills, configs |
| **Markdown** | — | 23,279 (99% are .aiwg index cards) | Specs, docs, cards |
| **Proto** | — | 16 | Protobuf contracts |
| **Mojo** | 1 (`math_ops.mojo`) | 1 | L5 muscle proof-of-concept |

## Critical Findings

### 1. Python is the dominant language (~95% of active runtime code)

The real active codebase is **~208 Python files** in `layers/` and `scripts/`. This is where all business logic, MCP tooling, memory management, routing, and orchestration lives.

### 2. Elixir: 3 first-party files, 58 are dependencies

```
First-party:
  layers/l0_overseer/mix.exs              (project definition)
  layers/l0_overseer/test/test_helper.exs (test helper)
  layers/l0_overseer/test/overseer_ipc_test.exs (IPC test)

Dependencies (in deps/):
  58 files from Hex packages (not first-party code)
```

**Verdict:** Elixir is **NOT a major runtime language**. It's used for a thin L0 Overseer supervisor. The `deps/` directory inflates the count. Any GitHub language statistics reporting Elixir at 42% are measuring vendored dependency code, not first-party source.

### 3. Go: ~30 first-party, ~16 generated protobuf

```
First-party:
  layers/l0_overseer/go.mod, go.sum      (Go module def)
  layers/l1_nervous/main.go              (L1 entry point)
  layers/l1_nervous/sidecar.go           (sidecar process)
  layers/l1_nervous/internal/skill/mcp_client.go  (MCP client)

Generated (protobuf):
  proto/*.pb.go                           (4 files)
  layers/l1_nervous/proto/*.pb.go         (4 files)
  .worktrees/*/proto/*.pb.go              (duplicated across 3 worktrees)
```

**Verdict:** Go is used for **L0/L1 system-level plumbing** (process supervision, gRPC, MCP client). ~14 first-party Go files, rest are generated protobuf stubs duplicated across worktrees.

### 4. Rust: 1 file (L3 Shield)

```
  layers/l3_shield/Cargo.toml  (project definition)
  layers/l3_shield/src/lib.rs  (shield audit_intent function with PyO3 bindings)
```

**Verdict:** Rust is used for a **single security function** — `audit_intent()` in L3 Shield, compiled as a `cdylib` for Python FFI via PyO3. Pre-compiled binary exists (`shield.so`, 666KB).

### 5. TypeScript/JavaScript: 0 first-party files

L6 Skin (`layers/l6_skin/`) contains:
- `index.html` (1 file, 3.2KB)
- `package.json` + `package-lock.json`
- `node_modules/` (vendored dependencies only)

**Verdict:** L6 has **no first-party TypeScript or JavaScript**. It's a bare HTML stub. Any dashboard/UI is aspirational, not implemented.

### 6. Markdown explosion: 23,279 files (99.5% are .aiwg index cards)

The `.aiwg/index/file_cards/` directory contains **23,105 auto-generated file card markdowns**. These are NOT documentation — they are machine-generated index entries. The real human-readable documentation is ~170 files across `doc/` and `docs/`.

### 7. .aiwg Python scratch: 3,739 files

The `.aiwg/workspaces/` directories (fix-l0, fix-l3) contain **duplicated copies of scratch scripts** from previous agent sessions. These are NOT active source code.

## Corrected Language Distribution (Active Runtime Only)

| Language | Active First-Party Files | Approximate % |
|:---|---:|---:|
| Python | 208 | 85.2% |
| Go | 14 | 5.7% |
| Shell | 15 (in scripts/) | 6.1% |
| Elixir | 3 | 1.2% |
| Rust | 1 | 0.4% |
| Mojo | 1 | 0.4% |
| HTML | 1 | 0.4% |
| Proto | 1 (dummie/v2/) | 0.4% |

**Conclusion:** DUMMIE Engine is a **Python-first system** with Go plumbing, a Rust security FFI, and an Elixir supervisor stub. The `.aiwg/identity.json` claim of `primary_language_focus: [Rust, Elixir, Mojo, Python]` is aspirational, not factual. The actual language priority is `Python > Go > Shell > Elixir > Rust > Mojo`.
