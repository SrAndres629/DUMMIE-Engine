# Swarm Orchestration Hardening Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the current memory, polyglot connector, and orchestration contract gaps so DUMMIE can safely move into multi-agent orchestration without stopping at every module boundary.

**Architecture:** Use a swarm execution model with one critical-path coordinator and independent worker lanes. The first lane fixes the L2-to-L5 execution contract because every real orchestration path depends on it; the other lanes harden tests, docs, and package boundaries in parallel. Event probability is used to choose the lowest-friction path first and defer low-value rewrites.

**Tech Stack:** Python/pytest/uv, Go, Rust/cargo, Node/npm, Arrow Flight, KuzuDB, MCP stdio, shell audit scripts.

---

## Code Quality Constraints

These constraints apply to every worker lane and block promotion if violated:

- Keep changes small and local to the owned files. Do not hide defects with compatibility shims unless the shim is the explicit public contract.
- Prefer clear interfaces over cross-layer shortcuts. L2 should depend on executor behavior, not on L5 transport naming.
- Preserve modular boundaries: L0 orchestration, L1 nervous/memory gateway, L2 brain planning, L3 shield validation, L5 muscle execution, and L6 skin surface must remain separately testable.
- Add tests at the contract boundary being fixed. A passing unit test with a fake is not enough when the defect is between real adapters.
- Avoid global path hacks, broad `sys.path` expansion, or resurrecting obsolete package names to make stale tests pass.
- Delete or isolate diagnostic/debug binaries from normal package builds.
- Keep docs/spec changes schema-valid and categorized; do not add generic frontmatter just to silence a validator if a real owner/status/category is known.
- Keep shell verification scripts idempotent: cleanup on success, failure, and interruption.
- Prefer boring names that describe responsibility: `execute`, `send_command`, `verify-industrial`, `test_daemon_real_mcp_driver_contract`.
- No unrelated refactors in worker lanes. If a file needs larger cleanup, create a follow-up task after the contract is green.

Review question for every patch:

```text
Does this make the next maintenance pass easier, or did it only make today's test pass?
```

## Probability Branch Map

Current evidence:
- `bash scripts/full_industrial_audit.sh`: PASS.
- `cd layers/l2_brain && uv run pytest -q tests`: PASS, 15 tests.
- `cd layers/l0_overseer && go test ./...`: PASS.
- `cd layers/l1_nervous && go test ./...`: FAIL, duplicate root `main`.
- `uv run --no-project --with pytest --with pyarrow pytest ...L1 tests...`: FAIL, stale `brain.*` imports.
- Real daemon smoke with L5 driver: FAIL, `MCPDriver` has no `execute`.
- `python3 scripts/validate_specs_docs.py`: FAIL, one malformed spec frontmatter.
- `cd layers/l6_skin && npm test`: FAIL, no test script.

Branch probabilities:
- **A. Direct contract fix succeeds quickly:** 0.72 probability. Add `MCPDriver.execute(...)` wrapper matching `BaseExecutor`, add one real-driver daemon test, keep daemon unchanged.
- **B. Daemon should call `send_command(...)` instead:** 0.18 probability. More invasive because daemon then depends on L5-specific naming.
- **C. Broader executor interface redesign needed:** 0.10 probability. Defer unless A fails under integration tests.

Lowest-friction path:
1. Choose Branch A first.
2. Run only contract tests.
3. If real-driver smoke passes, let other lanes proceed.
4. Only escalate to Branch B/C if A cannot satisfy existing `BaseExecutor`.

## Swarm Topology

Use one coordinator and five workers. Workers are independent by file ownership.

Coordinator owns:
- Integration sequencing.
- Final verification matrix.
- Conflict resolution.
- No broad refactors unless a worker proves a contract cannot hold.

Worker lanes:
- **Worker A - Execution Contract:** L2 daemon and L5 driver contract.
- **Worker B - L1 Package/Test Hygiene:** Go root package and stale Python tests.
- **Worker C - Memory Audit CI:** Makefile target and audit script stability.
- **Worker D - Docs/Spec Gate:** malformed spec frontmatter and validator.
- **Worker E - L6 Surface Gate:** minimal frontend test script or explicit smoke target.

Do not let workers edit each other's files. If a lane discovers it needs another lane's file, it reports back instead of patching across ownership.

## File Ownership

Worker A:
- Modify: `layers/l5_muscle/mcp_driver.py`
- Modify/Test: `layers/l2_brain/tests/test_daemon_hierarchical_planner.py` or create `layers/l2_brain/tests/test_daemon_real_mcp_driver_contract.py`
- Read-only: `layers/l2_brain/daemon.py`, `layers/l2_brain/auditor_port.py`

Worker B:
- Modify: `layers/l1_nervous/diag_kuzu.go`
- Modify/Test: `layers/l1_nervous/tests/test_causal_chaining.py`
- Modify/Test: `layers/l1_nervous/tests/test_causal_recovery.py`
- Read-only: `layers/l1_nervous/go.mod`, `layers/l2_brain/*`

Worker C:
- Modify: `Makefile`
- Modify: `scripts/full_industrial_audit.sh` only if verification shows cleanup/idempotency gaps.
- Read-only: `scripts/verify_compression.py`, `audit_report.json`

Worker D:
- Modify: `doc/specs/dummie_brain_v1.spec.md`
- Read-only: `scripts/validate_specs_docs.py`, `doc/specs/43_documentation_and_artifact_standards.md`

Worker E:
- Modify: `layers/l6_skin/package.json`
- Create optional: `layers/l6_skin/smoke.test.js` only if the package has a runnable JS test setup.
- Read-only: `layers/l6_skin/index.html`

## Chunk 1: Critical Contract Unlock

### Task 1: Add L5 Executor Compatibility

**Files:**
- Modify: `layers/l5_muscle/mcp_driver.py`
- Create: `layers/l2_brain/tests/test_daemon_real_mcp_driver_contract.py`

- [ ] **Step 1: Write failing test for real MCPDriver contract**

Create `layers/l2_brain/tests/test_daemon_real_mcp_driver_contract.py`:

```python
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
L5 = ROOT.parents[1] / "layers" / "l5_muscle"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(L5) not in sys.path:
    sys.path.insert(0, str(L5))

from daemon import DummieDaemon
from gateway_contract import GatewayRequest


class _Gateway:
    def __init__(self):
        self.calls = []

    async def call_tool(self, server_name, tool_name, arguments):
        self.calls.append((server_name, tool_name, arguments))
        return {"ok": True}


class _Bus:
    async def wait_for_request(self):
        raise NotImplementedError


@pytest.mark.asyncio
async def test_daemon_dispatches_task_through_real_mcp_driver():
    gateway = _Gateway()
    daemon = DummieDaemon("/tmp/ledger.jsonl", gateway, _Bus())
    request = GatewayRequest(
        session_id="S-REAL-L5",
        goal="real L5 contract smoke",
        dag_xml=(
            "<dag>"
            "<task id='t1' server='filesystem' tool='read'>"
            "<arguments>{\"path\":\"README.md\"}</arguments>"
            "</task>"
            "</dag>"
        ),
    )

    outcome = await daemon.process_request(request)

    assert outcome["status"] == "SUCCESS"
    assert gateway.calls == [
        (
            "dummie-brain",
            "exec_remote_tool",
            {
                "server_name": "filesystem",
                "tool_name": "read",
                "arguments": {"path": "README.md"},
            },
        )
    ]
```

- [ ] **Step 2: Run test and confirm current failure**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_daemon_real_mcp_driver_contract.py
```

Expected before implementation:

```text
FAILED ... 'MCPDriver' object has no attribute 'execute'
```

- [ ] **Step 3: Implement compatibility wrapper**

Modify `layers/l5_muscle/mcp_driver.py`:

```python
    async def execute(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await self.send_command(server_name, tool_name, arguments)
```

- [ ] **Step 4: Run focused contract test**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_daemon_real_mcp_driver_contract.py
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Run all L2 tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests
```

Expected:

```text
16 passed
```

- [ ] **Step 6: Commit**

```bash
git add layers/l5_muscle/mcp_driver.py layers/l2_brain/tests/test_daemon_real_mcp_driver_contract.py
git commit -m "fix: align daemon with real mcp driver contract"
```

## Chunk 2: L1 Package and Test Hygiene

### Task 2: Fix Go Root Package Collision

**Files:**
- Modify: `layers/l1_nervous/diag_kuzu.go`

- [ ] **Step 1: Reproduce failure**

Run:

```bash
cd layers/l1_nervous && go test ./...
```

Expected before fix:

```text
main redeclared in this block
```

- [ ] **Step 2: Add build tag to diagnostic binary**

Modify the top of `layers/l1_nervous/diag_kuzu.go`:

```go
//go:build diagnostic
// +build diagnostic

package main
```

- [ ] **Step 3: Verify package tests**

Run:

```bash
cd layers/l1_nervous && go test ./...
```

Expected:

```text
PASS or no test files, exit 0
```

- [ ] **Step 4: Verify diagnostic still builds when requested**

Run:

```bash
cd layers/l1_nervous && go run -tags diagnostic diag_kuzu.go
```

Expected:

```text
SUCCESS
```

or a real Kuzu path error if the local DB is unavailable. Do not block on DB state unless compile fails.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/diag_kuzu.go
git commit -m "fix: isolate l1 diagnostic main from package tests"
```

### Task 3: Retire or Port Stale L1 Python Tests

**Files:**
- Modify: `layers/l1_nervous/tests/test_causal_chaining.py`
- Modify: `layers/l1_nervous/tests/test_causal_recovery.py`

- [ ] **Step 1: Confirm stale imports**

Run:

```bash
uv run --no-project --with pytest --with pyarrow pytest -q \
  layers/l1_nervous/tests/test_causal_chaining.py \
  layers/l1_nervous/tests/test_causal_recovery.py
```

Expected before fix:

```text
ModuleNotFoundError: No module named 'brain'
```

- [ ] **Step 2: Classify tests**

Read both files and decide:
- If behavior exists in flat layout, port imports to current modules.
- If behavior belongs to removed architecture, mark as deleted or replaced with current contract tests.

- [ ] **Step 3: Prefer replacement over compatibility shim**

Do not recreate a fake `brain.*` package just to satisfy old tests. That hides migration debt.

- [ ] **Step 4: Run L1 Python tests**

Run:

```bash
uv run --no-project --with pytest --with pyarrow pytest -q layers/l1_nervous/tests
```

Expected:

```text
All collected tests pass, or obsolete tests are removed with replacement coverage.
```

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/tests/test_causal_chaining.py layers/l1_nervous/tests/test_causal_recovery.py
git commit -m "test: align l1 causal tests with flat architecture"
```

## Chunk 3: Industrial Audit as First-Class Gate

### Task 4: Add Makefile Target for Full Industrial Audit

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add audit target**

Modify `Makefile`:

```make
.PHONY: verify-industrial verify-all

verify-industrial:
	@echo "=== STARTING INDUSTRIAL AUDIT SUITE ==="
	@bash scripts/full_industrial_audit.sh

verify-all: verify-industrial
	@echo "=== VERIFY ALL COMPLETE ==="
```

If an existing `verify-industrial` target exists, replace the three scattered commands with `bash scripts/full_industrial_audit.sh` so there is a single source of truth.

- [ ] **Step 2: Run target**

Run:

```bash
make verify-industrial
```

Expected:

```text
AUDITORÍA COMPLETADA CON ÉXITO
```

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "chore: make industrial audit the verification gate"
```

## Chunk 4: Documentation Gate

### Task 5: Fix Malformed Spec Frontmatter

**Files:**
- Modify: `doc/specs/dummie_brain_v1.spec.md`

- [ ] **Step 1: Reproduce validator failure**

Run:

```bash
python3 scripts/validate_specs_docs.py
```

Expected before fix:

```text
missing or malformed YAML frontmatter
```

- [ ] **Step 2: Add minimal valid frontmatter**

At the top of `doc/specs/dummie_brain_v1.spec.md`, add:

```yaml
---
id: dummie_brain_v1
title: DUMMIE Brain V1
status: draft
owner: l2_brain
---
```

Adjust keys only if `scripts/validate_specs_docs.py` requires a different schema.

- [ ] **Step 3: Run validator**

Run:

```bash
python3 scripts/validate_specs_docs.py
```

Expected:

```text
DOC/SPEC VALIDATION PASSED
```

- [ ] **Step 4: Commit**

```bash
git add doc/specs/dummie_brain_v1.spec.md
git commit -m "docs: fix brain spec frontmatter"
```

## Chunk 5: L6 Surface Gate

### Task 6: Replace Failing NPM Test Placeholder

**Files:**
- Modify: `layers/l6_skin/package.json`

- [ ] **Step 1: Inspect package scripts**

Run:

```bash
cd layers/l6_skin && npm test
```

Expected before fix:

```text
Error: no test specified
```

- [ ] **Step 2: Add smoke test script**

If the app is plain HTML, set:

```json
"scripts": {
  "test": "node -e \"const fs=require('fs'); const html=fs.readFileSync('index.html','utf8'); if(!html.includes('<html')) throw new Error('index.html missing html root'); console.log('l6 smoke ok')\""
}
```

Preserve existing scripts if present.

- [ ] **Step 3: Run npm test**

Run:

```bash
cd layers/l6_skin && npm test
```

Expected:

```text
l6 smoke ok
```

- [ ] **Step 4: Commit**

```bash
git add layers/l6_skin/package.json
git commit -m "test: add l6 smoke test"
```

## Chunk 6: Final Integration Matrix

### Task 7: Run Full Verification Matrix

**Files:**
- No file changes unless a command exposes a real defect.

- [ ] **Step 1: Check git status**

Run:

```bash
git status --short
```

Expected:

```text
Only intended changes, or clean after commits.
```

- [ ] **Step 2: L2 tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests
```

Expected:

```text
16 passed
```

- [ ] **Step 3: L1 Go tests**

Run:

```bash
cd layers/l1_nervous && go test ./...
```

Expected:

```text
exit 0
```

- [ ] **Step 4: L1 Python tests**

Run:

```bash
uv run --no-project --with pytest --with pyarrow pytest -q layers/l1_nervous/tests
```

Expected:

```text
exit 0
```

- [ ] **Step 5: L0 Go tests**

Run:

```bash
cd layers/l0_overseer && go test ./...
```

Expected:

```text
exit 0
```

- [ ] **Step 6: L3 Rust tests**

Run:

```bash
cd layers/l3_shield && cargo test
```

Expected:

```text
test result: ok
```

- [ ] **Step 7: L6 smoke**

Run:

```bash
cd layers/l6_skin && npm test
```

Expected:

```text
exit 0
```

- [ ] **Step 8: Docs validator**

Run:

```bash
python3 scripts/validate_specs_docs.py
```

Expected:

```text
exit 0
```

- [ ] **Step 9: Industrial audit**

Run:

```bash
make verify-industrial
```

Expected:

```text
AUDITORÍA COMPLETADA CON ÉXITO
```

## Swarm Execution Rules

- Worker A starts first and blocks real orchestration promotion.
- Workers B, C, D, and E can run in parallel after Worker A writes the failing test.
- Coordinator must not merge any worker result until its focused verification command passes.
- If two workers need the same file, stop and reassign ownership before editing.
- If a worker hits a third failed fix attempt, stop that lane and escalate architecture instead of patching more.

## Promotion Criteria

The project is ready to start the next orchestration phase when:
- Real daemon-to-L5 contract test passes.
- L1 Go and Python tests no longer fail due to package/layout drift.
- Memory online audit is reachable through `make verify-industrial`.
- Documentation validator passes.
- L6 has at least a smoke gate instead of a failing placeholder.
- Each worker patch keeps ownership boundaries clear, avoids obsolete compatibility layers, and leaves the affected module easier to understand than before.

After promotion, the first orchestration milestone should be narrow: one saga with two MCP tool calls, one intentional failure, and verified compensation.
