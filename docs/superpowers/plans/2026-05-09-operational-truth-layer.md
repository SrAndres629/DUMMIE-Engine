# Operational Truth Layer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first snowball repair layer so DUMMIE can measure what is real, degraded, blocked, or aspirational before choosing the next repair.

**Architecture:** Add a small pure L2 truth model, focused collectors that reuse existing router/swarm/reward/memory components, a CLI report, and one L1 MCP tool. The layer reports evidence first and avoids broad runtime changes.

**Tech Stack:** Python 3, pytest, FastMCP, KuzuRepository, existing L2 router/discovery/ledger modules, Makefile.

---

## File Structure

- Create: `layers/l2_brain/operational_truth.py`  
  Owns `TruthStatus`, `TruthCheck`, `TruthReport`, and pure serialization helpers.
- Create: `layers/l2_brain/operational_truth_collectors.py`  
  Owns probe functions for runtime, imports, Kuzu, model discovery, router, swarm ledger, reward ledger, action graph, L0, L3, L5, and L6.
- Create: `layers/l2_brain/tests/test_operational_truth.py`  
  Unit tests for statuses, summaries, serialization, and graceful degraded checks.
- Create: `scripts/dummie_truth.py`  
  CLI entrypoint that prints text or JSON and writes `.aiwg/reports/operational_truth.json`.
- Modify: `layers/l1_nervous/tools_impl/core.py`  
  Registers `operational_truth_report`.
- Modify: `Makefile`  
  Adds `verify-truth`.

Do not modify `model_router.py`, `neuron_ledger.py`, `action_graph.py`, or `swarm.py` in this phase unless a test proves a minimal compatibility bug blocks truth collection.

## Chunk 1: Truth Data Model

### Task 1: Add Pure Truth Types

**Files:**
- Create: `layers/l2_brain/operational_truth.py`
- Create: `layers/l2_brain/tests/test_operational_truth.py`

- [ ] **Step 1: Write failing tests for status summaries**

Create `layers/l2_brain/tests/test_operational_truth.py`:

```python
from operational_truth import TruthCheck, TruthReport, TruthStatus


def test_truth_report_counts_statuses():
    report = TruthReport(
        repo_root="/repo",
        checks=[
            TruthCheck("l1.gateway.import", "L1", TruthStatus.PASS, ["import ok"]),
            TruthCheck("l3.budget", "L3", TruthStatus.DEGRADED, ["stub auditor"]),
            TruthCheck("l0.daemon", "L0", TruthStatus.BLOCKED, ["not running"]),
        ],
    )

    assert report.summary() == {
        "PASS": 1,
        "DEGRADED": 1,
        "BLOCKED": 1,
        "UNKNOWN": 0,
    }
```

- [ ] **Step 2: Run test and verify it fails**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: FAIL because `operational_truth` does not exist.

- [ ] **Step 3: Implement minimal data model**

Add `layers/l2_brain/operational_truth.py`:

```python
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any


class TruthStatus(str, Enum):
    PASS = "PASS"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass
class TruthCheck:
    name: str
    layer: str
    status: TruthStatus
    evidence: list[str] = field(default_factory=list)
    command: str = ""
    error: str = ""
    next_repair: str = ""


@dataclass
class TruthReport:
    repo_root: str
    checks: list[TruthCheck]
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def summary(self) -> dict[str, int]:
        counts = {status.value: 0 for status in TruthStatus}
        for check in self.checks:
            counts[check.status.value] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "repo_root": self.repo_root,
            "summary": self.summary(),
            "checks": [asdict(check) for check in self.checks],
        }
```

- [ ] **Step 4: Run test and verify it passes**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: PASS.

## Chunk 2: Collectors Reusing Existing Work

### Task 2: Add Collectors For Current Router/Swarm/Reward Infrastructure

**Files:**
- Create: `layers/l2_brain/operational_truth_collectors.py`
- Modify: `layers/l2_brain/tests/test_operational_truth.py`

- [ ] **Step 1: Write tests for graceful router and ledger probes**

Append:

```python
from pathlib import Path

from operational_truth import TruthStatus
from operational_truth_collectors import collect_truth


def test_collect_truth_reports_existing_neuron_and_swarm_assets(tmp_path: Path):
    repo = tmp_path
    (repo / "layers/l2_brain").mkdir(parents=True)
    (repo / "layers/l1_nervous/tools_impl").mkdir(parents=True)
    (repo / ".aiwg/memory").mkdir(parents=True)
    (repo / "layers/l2_brain/neuron_ledger.py").write_text("class NeuronLedger: pass\n")
    (repo / "layers/l2_brain/action_graph.py").write_text("class ActionGraph: pass\n")
    (repo / "layers/l1_nervous/tools_impl/swarm.py").write_text("def register_swarm_tools(): pass\n")

    report = collect_truth(str(repo), include_slow=False)
    by_name = {check.name: check for check in report.checks}

    assert by_name["l2.neuron_ledger.file"].status == TruthStatus.PASS
    assert by_name["l2.action_graph.file"].status == TruthStatus.PASS
    assert by_name["l1.swarm_tools.file"].status == TruthStatus.PASS
```

- [ ] **Step 2: Run test and verify it fails**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: FAIL because collectors do not exist.

- [ ] **Step 3: Implement file and import collectors**

Create `layers/l2_brain/operational_truth_collectors.py`:

```python
from __future__ import annotations

import importlib
import os
from pathlib import Path

from operational_truth import TruthCheck, TruthReport, TruthStatus


def _file_check(repo: Path, name: str, layer: str, rel_path: str, next_repair: str = "") -> TruthCheck:
    path = repo / rel_path
    if path.exists():
        return TruthCheck(name, layer, TruthStatus.PASS, [f"found {rel_path}"])
    return TruthCheck(name, layer, TruthStatus.BLOCKED, [f"missing {rel_path}"], next_repair=next_repair)


def _import_check(name: str, layer: str, module: str, next_repair: str = "") -> TruthCheck:
    try:
        importlib.import_module(module)
        return TruthCheck(name, layer, TruthStatus.PASS, [f"import {module} ok"])
    except Exception as exc:
        return TruthCheck(name, layer, TruthStatus.BLOCKED, [], error=str(exc), next_repair=next_repair)


def collect_truth(repo_root: str, include_slow: bool = False) -> TruthReport:
    repo = Path(repo_root)
    checks: list[TruthCheck] = [
        _file_check(repo, "l2.model_router.file", "L2", "layers/l2_brain/model_router.py"),
        _file_check(repo, "l2.model_discovery.file", "L2", "layers/l2_brain/model_discovery.py"),
        _file_check(repo, "l2.neuron_ledger.file", "L2", "layers/l2_brain/neuron_ledger.py"),
        _file_check(repo, "l2.action_graph.file", "L2", "layers/l2_brain/action_graph.py"),
        _file_check(repo, "l2.supervisor_protocol.file", "L2", "layers/l2_brain/supervisor_protocol.py"),
        _file_check(repo, "l1.swarm_tools.file", "L1", "layers/l1_nervous/tools_impl/swarm.py"),
        _file_check(repo, "l0.dummied.binary", "L0", "layers/l0_overseer/dummied", "build and start dummied"),
        _file_check(repo, "l3.topological_auditor.file", "L3", "layers/l3_shield/topological_auditor.py"),
        _file_check(repo, "l5.mcp_driver.file", "L5", "layers/l5_muscle/mcp_driver.py"),
        _file_check(repo, "l6.skin.package", "L6", "layers/l6_skin/package.json"),
    ]

    l2_path = repo / "layers/l2_brain"
    if str(l2_path) not in os.sys.path:
        os.sys.path.insert(0, str(l2_path))

    checks.extend(
        [
            _import_check("l2.model_router.import", "L2", "model_router"),
            _import_check("l2.neuron_ledger.import", "L2", "neuron_ledger"),
            _import_check("l2.action_graph.import", "L2", "action_graph"),
        ]
    )

    return TruthReport(repo_root=str(repo), checks=checks)
```

- [ ] **Step 4: Run tests**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: PASS.

## Chunk 3: Runtime And Model Discovery Probes

### Task 3: Add Runtime, Kuzu, And Model Tier Checks

**Files:**
- Modify: `layers/l2_brain/operational_truth_collectors.py`
- Modify: `layers/l2_brain/tests/test_operational_truth.py`

- [ ] **Step 1: Add tests for no-crash runtime probes**

Append:

```python
def test_collect_truth_never_crashes_when_runtime_is_absent(tmp_path: Path):
    report = collect_truth(str(tmp_path), include_slow=True)
    assert report.summary()["UNKNOWN"] >= 0
    assert all(check.name for check in report.checks)
```

- [ ] **Step 2: Implement probes as evidence-only checks**

Add functions:

```python
def _process_check(name: str, layer: str, needle: str) -> TruthCheck:
    try:
        import subprocess
        out = subprocess.check_output(["ps", "-eo", "cmd"], text=True, timeout=2)
        if needle in out:
            return TruthCheck(name, layer, TruthStatus.PASS, [f"process contains {needle}"])
        return TruthCheck(name, layer, TruthStatus.DEGRADED, [f"no live process containing {needle}"])
    except Exception as exc:
        return TruthCheck(name, layer, TruthStatus.UNKNOWN, error=str(exc))
```

Add checks for:

- `mcp_server.py`
- `dummied`
- `nats-server`
- `ollama serve`

Add model discovery check using `ModelDiscoveryService.discover_all()` only when `include_slow=True`; otherwise mark it `UNKNOWN` with next repair `run include_slow truth report`.

- [ ] **Step 3: Run focused tests**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: PASS.

## Chunk 4: CLI Report

### Task 4: Add `scripts/dummie_truth.py`

**Files:**
- Create: `scripts/dummie_truth.py`
- Create/Modify: `tests/test_operational_truth_cli.py` or keep under `layers/l2_brain/tests/test_operational_truth.py`

- [ ] **Step 1: Write CLI smoke test**

Add:

```python
import json
import subprocess


def test_dummie_truth_cli_json_smoke():
    out = subprocess.check_output(
        ["python3", "scripts/dummie_truth.py", "--json"],
        text=True,
    )
    payload = json.loads(out)
    assert "summary" in payload
    assert "checks" in payload
```

- [ ] **Step 2: Implement CLI**

Create `scripts/dummie_truth.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "layers" / "l2_brain"
sys.path.insert(0, str(L2))

from operational_truth_collectors import collect_truth


def _format_text(report) -> str:
    lines = ["=== DUMMIE OPERATIONAL TRUTH ===", f"Repo: {report.repo_root}", f"Summary: {report.summary()}"]
    for check in report.checks:
        evidence = "; ".join(check.evidence) if check.evidence else check.error
        lines.append(f"- [{check.status.value}] {check.layer} {check.name}: {evidence}")
        if check.next_repair:
            lines.append(f"  next: {check.next_repair}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-slow", action="store_true")
    args = parser.parse_args()

    report = collect_truth(str(ROOT), include_slow=args.include_slow)
    report_path = ROOT / ".aiwg" / "reports" / "operational_truth.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report.to_dict(), indent=2) + "\n")

    if args.json:
        print(json.dumps(report.to_dict()))
    else:
        print(_format_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run CLI**

Run:

```bash
python3 scripts/dummie_truth.py
python3 scripts/dummie_truth.py --json
```

Expected: text report prints, JSON parses, `.aiwg/reports/operational_truth.json` is written.

## Chunk 5: MCP Surface

### Task 5: Expose Operational Truth Through L1 Core Tools

**Files:**
- Modify: `layers/l1_nervous/tools_impl/core.py`
- Modify: `layers/l1_nervous/tests/test_runtime_contracts.py` or create `layers/l1_nervous/tests/test_operational_truth_tool.py`

- [ ] **Step 1: Write test that core registration includes the tool**

Create a small FastMCP fake or follow the pattern in `layers/l1_nervous/tests/test_read_spec.py`. Assert a registered tool named `operational_truth_report` exists.

- [ ] **Step 2: Implement tool**

In `register_core_tools`, add:

```python
@mcp.tool()
async def operational_truth_report(format: str = "text", include_slow: bool = False) -> str:
    """[TRUTH] Reports real operational state of DUMMIE Engine."""
    import json
    import os
    import sys

    l2_path = os.path.join(root_dir, "layers", "l2_brain")
    if l2_path not in sys.path:
        sys.path.insert(0, l2_path)

    from operational_truth_collectors import collect_truth

    report = collect_truth(root_dir, include_slow=include_slow)
    if format == "json":
        return json.dumps(report.to_dict(), indent=2)

    lines = ["=== DUMMIE OPERATIONAL TRUTH ===", f"Summary: {report.summary()}"]
    for check in report.checks:
        evidence = "; ".join(check.evidence) if check.evidence else check.error
        lines.append(f"- [{check.status.value}] {check.layer} {check.name}: {evidence}")
    return "\n".join(lines)
```

- [ ] **Step 3: Run L1 focused tests**

Run:

```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l1_nervous/tests/test_read_spec.py layers/l1_nervous/tests/test_runtime_contracts.py
```

Expected: PASS.

## Chunk 6: Make Target And Promotion Criteria

### Task 6: Add `verify-truth`

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add Makefile target**

Add:

```make
.PHONY: verify-truth

verify-truth:
	@python3 scripts/dummie_truth.py
```

- [ ] **Step 2: Run verification**

Run:

```bash
make verify-truth
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
```

Expected: report prints and tests pass.

## Chunk 7: First Snowball Use

### Task 7: Use Truth Report To Select Next Repair

**Files:**
- Read: `.aiwg/reports/operational_truth.json`
- Read: `layers/l2_brain/tests/test_model_router.py`
- Read: `layers/l3_shield/tests/test_topological_auditor.py`
- Read: `layers/l2_brain/tests/test_daemon_cognitive_preflight.py`

- [ ] **Step 1: Run the truth report with slow checks**

Run:

```bash
python3 scripts/dummie_truth.py --include-slow
```

- [ ] **Step 2: Pick the lowest-friction blocker**

Use this priority:

1. A blocker that prevents truth collection itself.
2. A blocker that prevents model discovery/router defaults.
3. A blocker that prevents L3 topological safety.
4. A blocker that prevents daemon preflight/saga.
5. A degraded ledger that prevents reward/action persistence.

- [ ] **Step 3: Create the next repair plan**

Create a follow-up plan named:

`docs/superpowers/plans/YYYY-MM-DD-operational-truth-next-repair.md`

It must start from actual `operational_truth.json` evidence, not assumptions.

## Verification Matrix

Run these before promoting Phase A:

```bash
python3 scripts/dummie_truth.py --json
python3 scripts/dummie_truth.py --include-slow
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_operational_truth.py
layers/l2_brain/.venv/bin/python -m pytest -q layers/l1_nervous/tests/test_read_spec.py layers/l1_nervous/tests/test_runtime_contracts.py
make verify-truth
```

Expected:

- Commands exit 0.
- `.aiwg/reports/operational_truth.json` exists.
- Known incomplete areas are reported as `DEGRADED` or `BLOCKED`, not hidden.
- Router/swarm/reward components are reported as existing assets and measured for connectivity.

## Follow-Up Snowball Repairs

After Phase A, execute the next repairs in this order unless the truth report proves a different blocker is lower-friction:

1. Fix `ModelRouter` default/discovery mismatch so `ModelRouter()` never returns `model_id="none"` when Ollama/defaults are available.
2. Fix `TopologicalAuditor` to support both `<task><depends_on>` and `<edge source target>` DAG formats.
3. Fix `DummieDaemon` cognitive preflight contract or remove the stale flag path from runtime until implemented.
4. Persist `NeuronLedger` and make router ranking use reputation.
5. Normalize swarm, action, token, and reward events into one causal ledger view.
6. Build the minimal stable cognitive loop.
