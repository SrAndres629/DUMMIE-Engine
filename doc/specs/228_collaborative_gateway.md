---
status: SUPERSEDED
claims:
- id: six_modes
  description: '6 modos: auto, discover, execute, plan, confirm, reject, list, parallel'
  severity: critical
- id: plan_mode_no_execute
  description: Modo plan muestra que se hara sin ejecutar
  severity: high
implementations:
- file: layers/l1_nervous/tools.py
  function: dummie_process
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Collaborative Gateway: Plan-Then-Execute

**Date:** 2026-05-26
**Phase:** 2a
**Requires reboot:** No
**Depends on:** Spec 223 (tools collapse)
**Files modified:** `layers/l1_nervous/tools.py`

## 1. Purpose

Transform the MetaGateway from a silent black-box dispatcher into a collaborative partner that shares its reasoning with the LLM agent before executing. The gateway proposes a plan; the agent confirms or rejects it. This eliminates the "blind" tool call where the agent has no visibility into what the gateway will do.

## 2. Problem

Currently `dummie_process` is a black box:
```
Agent: dummie_process("run tdd on user model")
Gateway: [internally: route → match skill → execute 5 steps → compact result]
Agent: receives "{status: pass, coverage: 87%}" but never knew what happened
```

The agent has zero visibility into gateway reasoning. If the gateway makes a wrong routing decision, the agent cannot intervene. If the gateway executes something expensive the agent didn't intend, there's no pre-approval step.

## 3. Design: Plan-then-Execute

### 3.1 New mode: "plan"

```python
dummie_process(intent="run tdd on user model", mode="plan")
```

Returns a human-readable plan:

```json
{
  "mode": "plan",
  "intent": "run tdd on user model",
  "plan": {
    "domain": "workspace_io",
    "skill": "tdd",
    "confidence": 0.92,
    "strategy": "cache_hit",
    "steps": [
      {
        "id": "find_tests",
        "description": "Find test files matching *_test.py",
        "server": "filesystem",
        "tool": "search_files",
        "estimated_tokens": 200
      },
      {
        "id": "read_tests",
        "description": "Read existing test files",
        "server": "filesystem",
        "tool": "read_text_file",
        "depends_on": ["find_tests"],
        "estimated_tokens": 800
      },
      {
        "id": "run_tests",
        "description": "Execute pytest on test files",
        "server": "shell",
        "tool": "execute_command",
        "depends_on": ["read_tests"],
        "estimated_tokens": 500
      }
    ],
    "total_estimated_tokens": 1500,
    "context_budget_used": 1500,
    "context_budget_available": 4000
  }
}
```

### 3.2 New mode: "confirm"

The agent sends back the plan with `mode="confirm"`:

```python
dummie_process(intent="run tdd on user model", mode="confirm", plan={...})
```

The gateway executes the pre-approved plan and returns the compact result.

### 3.3 New mode: "reject"

The agent can reject and suggest alternatives:

```python
dummie_process(intent="run tdd on user model", mode="reject", reason="Skip step 3, tests already passing")
```

Gateway adapts accordingly or returns error.

### 3.4 Mode "auto" (unchanged)

```python
dummie_process(intent="run tdd on user model", mode="auto")
```

High confidence (≥0.85): plan silently, execute, return result.
Low confidence (<0.85): return plan and let agent decide (implicit "plan" mode).

## 4. Implementation

### 4.1 Modified dummie_process flow

```python
async def dummie_process(intent: str, mode: str = "auto") -> str:
    # ... existing preamble (cache check, validation) ...

    # NEW: Plan mode
    if mode == "plan":
        plan = await self._build_plan(intent)
        return json.dumps({"mode": "plan", "intent": intent, "plan": plan})

    # NEW: Confirm mode — execute pre-approved plan
    if mode == "confirm":
        if not arguments or "plan" not in arguments:
            return json.dumps({"error": "confirm mode requires plan"})
        result = await self._execute_plan(arguments["plan"])
        return json.dumps({"mode": "confirm", "result": result})

    # NEW: Reject mode — agent disagrees with plan
    if mode == "reject":
        reason = arguments.get("reason", "unspecified")
        logger.info("Agent rejected plan for '%s': %s", intent[:50], reason)
        # Offer to re-route with different approach
        return json.dumps({
            "mode": "reject",
            "message": f"Plan rejected: {reason}. Call again with mode=plan for re-routing."
        })

    # Auto mode (existing)
    plan = await self._build_plan(intent)
    
    if plan["confidence"] >= 0.85:
        # High confidence → execute silently
        result = await self._execute_plan(plan)
        return json.dumps(result)
    else:
        # Low confidence → share plan, let agent decide
        return json.dumps({
            "mode": "plan",
            "intent": intent,
            "plan": plan,
            "suggestion": "Low confidence routing. Review plan and call with mode=confirm or mode=reject."
        })
```

### 4.2 Plan building (new helper)

```python
async def _build_plan(self, intent: str) -> dict:
    """Build execution plan without executing."""
    _, proxy_mgr = setup_internal()

    # Cache check
    cached = await self.cache.get(intent)
    if cached:
        return cached.get("plan", cached)

    # Budget selection
    budget = self.budget_router.get_tools_for_budget(context_budget)
    
    # Route
    route = await self.smart_router.route(intent, budget)
    
    # Skill match
    skill = await self.skill_executor.match(intent)
    
    plan = {
        "domain": route.get("domain"),
        "skill": skill.skill_id if skill else None,
        "confidence": route.get("confidence", 0.0),
        "strategy": route.get("strategy", "unknown"),
        "steps": [],
        "total_estimated_tokens": 0,
    }

    if skill:
        for step in skill.steps:
            plan["steps"].append({
                "id": step.step_id,
                "description": step.description,
                "server": step.server,
                "tool": step.tool,
                "depends_on": step.depends_on,
                "estimated_tokens": self._estimate_tokens(step),
            })
        plan["total_estimated_tokens"] = sum(s["estimated_tokens"] for s in plan["steps"])

    return plan
```

### 4.3 Plan execution (existing but formalized)

```python
async def _execute_plan(self, plan: dict) -> dict:
    """Execute a pre-built plan."""
    if plan.get("skill"):
        skill = self.skill_executor.get_skill(plan["skill"])
        if skill:
            return await self.skill_executor.execute(skill, plan.get("intent", ""))
    
    # Single tool fallback
    step = plan["steps"][0] if plan["steps"] else {}
    if step:
        _, proxy_mgr = setup_internal()
        return await proxy_mgr.call_tool(step["server"], step["tool"], step)
    
    return {"error": "No executable steps in plan"}
```

## 5. Token estimation

```python
def _estimate_tokens(self, step: dict) -> int:
    """Conservative token estimate for a step's output."""
    base = 200  # tool call overhead + result envelope
    
    if step["server"] == "filesystem":
        if "read" in step["tool"]:
            return base + 800  # file contents can be large
        return base + 100
    elif step["server"] == "shell":
        return base + 500  # command output
    elif step["server"] == "github":
        return base + 300
    elif step["server"] == "browser-use":
        return base + 2000  # HTML content
    
    return base + 200
```

## 6. Success Criteria

| Metric | Before | After |
|--------|--------|-------|
| Agent visibility into gateway actions | 0% (black box) | 100% (plan shown) |
| Agent can reject bad plans | No | Yes (mode=reject) |
| High-confidence skills still automatic | N/A | Yes (mode=auto + confidence≥0.85) |
| Token cost of plan display | 0 | ~200-500 (plan steps) |
| Backward compatibility | N/A | Yes (mode="auto" unchanged) |

## 7. Mode decision logic

```
dummie_process(intent, mode)
  │
  ├── mode="plan"     → show plan, don't execute
  ├── mode="confirm"  → execute provided plan
  ├── mode="reject"   → agent disagrees, gateway adapts
  └── mode="auto"     
        ├── confidence ≥ 0.85 → execute silently
        └── confidence < 0.85 → show plan (implicit plan mode)
```