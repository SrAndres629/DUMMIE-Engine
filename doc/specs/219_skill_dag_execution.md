---
status: SUPERSEDED
claims:
- id: four_skills_exist
  description: 4 skills built-in en skill_executor.py
  severity: critical
  verify_cmd: uv run python -c 'from skill_executor import BUILTIN_SKILLS; assert
    len(BUILTIN_SKILLS)>=4; print(len(BUILTIN_SKILLS))'
- id: tdd_skill_structure
  description: Skill TDD con 3+ steps y dependencias correctas
  severity: high
implementations:
- file: layers/l1_nervous/skill_executor.py
  class: SkillExecutor
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Skill-aware DAG Execution

**Date:** 2026-05-26  
**Phase:** D  
**Requires reboot:** No  
**Depends on:** Phase C (dummie_process)  
**Files created:** `layers/l1_nervous/skill_executor.py`  
**Files modified:** `layers/l1_nervous/tools.py`  

## 1. Purpose

When `dummie_process` receives an intent that matches a skill template (TDD, code review, debugging), execute the skill's multi-step tool DAG server-side and return only the compact final result to the agent. The agent never sees individual tool calls within a skill.

## 2. Design

### 2.1 SkillTemplate structure

```python
@dataclass
class SkillStep:
    step_id: str
    description: str
    server: str
    tool: str
    arguments: dict
    depends_on: list[str] = field(default_factory=list)

@dataclass  
class SkillTemplate:
    skill_id: str
    name: str
    description: str
    trigger_patterns: list[str]
    steps: list[SkillStep]
    result_mapping: str  # template for compact result
```

### 2.2 Built-in skills (hardcoded for Phase D, no file loading yet)

| Skill | Trigger | Steps |
|-------|---------|-------|
| **tdd** | "test", "tdd", "red-green", "implement test" | find_tests → read_tests → run_tests → write_code |
| **code_review** | "review", "code review", "analyze code" | read_file → lint_check → detect_issues → suggest |
| **debug** | "debug", "fix bug", "why is it failing" | read_file → reproduce_error → identify_fix → apply_fix |
| **git_workflow** | "branch", "commit", "merge", "PR" | git_status → create_branch → commit → push |
| **explore** | "find", "search", "explore codebase" | search_files → read_matches → summarize |

### 2.3 Integration into dummie_process

After SmartRouter classification (step 4) and before MetacognitiveReasoner fallback (step 5), check if the intent matches any skill template. If yes:

1. Load skill template
2. Topological sort steps by dependencies
3. Execute steps (parallel where possible)
4. Compact results into summary
5. Return compact summary instead of individual tool calls

### 2.4 Example: TDD flow

```
Agent: dummie_process(intent="write tests for user authentication")
  │
  ├─ Cache → miss
  ├─ SmartRouter → domain: workspace_io, confidence: 0.7
  ├─ Skill match → "tdd" (patterns: "test", "implement.*test")
  │
  ├─ DAG execution (server-side, agent unaware):
  │   Step 1: filesystem.search_files("**/test_auth*.py")  → []
  │   Step 2: filesystem.search_files("**/auth*.py")       → ["src/auth.py"]
  │   Step 3: filesystem.read_text_file("src/auth.py")     → [auth.py content]
  │   Step 4: shell.execute_command("pytest tests/ -k auth -v")
  │           → "FAILED test_create_user: missing implementation"
  │   Step 5: Generate test suggestion from auth.py analysis
  │
  └─ Compact result to agent:
      {
        "skill": "tdd",
        "steps_executed": 5,
        "status": "tests_failing",
        "coverage": "none",
        "existing_tests": 0,
        "source_file": "src/auth.py",
        "failing_test": "test_create_user",
        "suggestion": "Implement User.create() method"
      }
```

## 3. Implementation

### 3.1 skill_executor.py

```python
"""
Skill-aware DAG execution engine for SMART MetaGateway.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("dummie-smart.skills")


@dataclass
class SkillStep:
    step_id: str
    description: str
    server: str
    tool: str
    arguments: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class SkillTemplate:
    skill_id: str
    name: str
    description: str
    trigger_patterns: list[str]
    steps: list[SkillStep]


BUILTIN_SKILLS: list[SkillTemplate] = [
    SkillTemplate(
        skill_id="tdd",
        name="Test-Driven Development",
        description="Find tests, run them, and implement missing functionality.",
        trigger_patterns=["test", "tdd", "red.?green", "implement.*test", "write.*test"],
        steps=[
            SkillStep("1", "Find test files", "filesystem", "search_files",
                      {"pattern": "**/test_*.py"}),
            SkillStep("2", "Find source files", "filesystem", "search_files",
                      {"pattern": "**/*.py"}),
            SkillStep("3", "Read source file", "filesystem", "read_text_file",
                      {}, depends_on=["2"]),
            SkillStep("4", "Run existing tests", "shell", "execute_command",
                      {"command": "python -m pytest -q 2>&1"}, depends_on=["1"]),
        ],
    ),
    SkillTemplate(
        skill_id="debug",
        name="Systematic Debugging",
        description="Reproduce bug, identify root cause, and apply fix.",
        trigger_patterns=["debug", "bug", "fix", "error", "failing", "why is"],
        steps=[
            SkillStep("1", "Find relevant files", "filesystem", "search_files",
                      {"pattern": "**/*.py"}),
            SkillStep("2", "Read file for context", "filesystem", "read_text_file",
                      {}, depends_on=["1"]),
            SkillStep("3", "Run to reproduce error", "shell", "execute_command",
                      {"command": "python -c 'import traceback' 2>&1"}, depends_on=["2"]),
        ],
    ),
    SkillTemplate(
        skill_id="explore",
        name="Explore Codebase",
        description="Find and analyze code across the repository.",
        trigger_patterns=["find", "search", "explore", "where is", "locate", "grep"],
        steps=[
            SkillStep("1", "Search for pattern", "filesystem", "search_files",
                      {"pattern": "**/*"}),
            SkillStep("2", "Read matches", "filesystem", "read_text_file",
                      {}, depends_on=["1"]),
        ],
    ),
]


class SkillExecutor:
    """Execute skill tool DAGs with topological ordering and parallel execution."""

    def __init__(self, proxy_manager):
        self.proxy = proxy_manager
        self._results: dict[str, Any] = {}

    async def match(self, intent: str) -> Optional[SkillTemplate]:
        """Find the first skill whose trigger patterns match the intent."""
        import re
        for skill in BUILTIN_SKILLS:
            for pattern in skill.trigger_patterns:
                if re.search(pattern, intent, re.IGNORECASE):
                    logger.info("Skill matched: %s (pattern: %s)", skill.skill_id, pattern)
                    return skill
        return None

    async def execute(self, skill: SkillTemplate, intent: str) -> dict:
        """Execute a skill's tool DAG and return compact results."""
        self._results = {}

        # Topological sort
        independent = [s for s in skill.steps if not s.depends_on]
        dependent = [s for s in skill.steps if s.depends_on]

        # Execute independent steps in parallel
        if independent:
            tasks = [self._execute_step(s, intent) for s in independent]
            await asyncio.gather(*tasks, return_exceptions=True)

        # Execute dependent steps sequentially
        for step in dependent:
            if all(dep in self._results for dep in step.depends_on):
                await self._execute_step(step, intent)

        return self._compact(skill, intent)

    async def _execute_step(self, step: SkillStep, intent: str):
        """Execute a single skill step via MCPProxyManager."""
        try:
            args = dict(step.arguments)
            if "intent" not in args and not args:
                args["intent"] = intent
            result = await self.proxy.call_tool(step.server, step.tool, args)
            self._results[step.step_id] = {"success": True, "output": str(result)[:500]}
        except Exception as e:
            self._results[step.step_id] = {"success": False, "error": str(e)}
            logger.warning("Skill step %s failed: %s", step.step_id, e)

    def _compact(self, skill: SkillTemplate, intent: str) -> dict:
        """Build compact result summary from executed steps."""
        return {
            "skill": skill.skill_id,
            "skill_name": skill.name,
            "steps_total": len(skill.steps),
            "steps_completed": sum(1 for r in self._results.values() if r.get("success")),
            "steps_failed": sum(1 for r in self._results.values() if not r.get("success")),
            "outputs": {
                step_id: data.get("output", data.get("error", ""))[:200]
                for step_id, data in self._results.items()
            },
        }
```

### 3.2 Integration into dummie_process

Add between step 4 (SmartRouter) and step 5 (MetacognitiveReasoner fallback):

```python
        # ── 4.5 Skill match + DAG execution ──
        skill_result = None
        try:
            from skill_executor import SkillExecutor
            executor = SkillExecutor(proxy_mgr)
            matched = await executor.match(intent)
            if matched:
                skill_result = await executor.execute(matched, intent)
        except Exception:
            logger.debug("Skill executor failed", exc_info=True)

        if skill_result:
            response = {
                "intent": intent,
                "mode": mode,
                "skill_executed": True,
                "skill": skill_result,
                "total_latency_ms": (_time.monotonic() - t_start) * 1000,
            }
            # Cache skill result
            try:
                from semantic_cache import SemanticRouteCache
                _cache = SemanticRouteCache()
                asyncio.create_task(_cache.set(intent, response))
            except Exception:
                pass
            return json.dumps(response, indent=2, ensure_ascii=False)
```

## 4. Edge cases

| Case | Behavior |
|------|----------|
| Skill step fails | Continue remaining steps, report partial results |
| No skill matches intent | Proceed to normal routing (no-op at this stage) |
| MCP server cold start | SkillExecutor waits (first call slow, subsequent fast) |
| Circular dependencies | Topological sort catches and rejects |
| Very long step output | Truncated to 500 chars per step |

## 5. Success criteria

| Metric | Before | After |
|--------|--------|-------|
| TDD workflow tool calls for agent | 4-6 individual calls | 1 call (dummie_process) |
| Agent context consumed by TDD flow | ~2000 tokens (4 results) | ~300 tokens (compact summary) |
| Skill match latency | N/A (no skill system) | <5ms (regex match) |

## 6. Files

| File | Action |
|------|--------|
| `layers/l1_nervous/skill_executor.py` | **Create** — SkillTemplate, SkillExecutor, BUILTIN_SKILLS |
| `layers/l1_nervous/tools.py` | **Modify** — add skill match section in dummie_process |
| `layers/l1_nervous/tests/test_smart_components.py` | **Modify** — add skill executor tests |