---
status: SUPERSEDED
claims:
- id: skill_list_mode
  description: mode=list lista skills disponibles
  severity: critical
- id: skill_explicit_invocation
  description: Parametro skill= permite invocacion deliberada
  severity: high
implementations:
- file: layers/l1_nervous/skill_executor.py
  class: SkillExecutor
  type: primary
- file: layers/l1_nervous/tools.py
  function: dummie_process
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Skill Catalog Exposure + Deliberate Invocation

**Date:** 2026-05-26  
**Phase:** 2c  
**Requires reboot:** No  
**Depends on:** Spec 228 (collaborative gateway plan/confirm)  
**Files modified:** `tools.py`, `skill_executor.py`

## 1. Purpose

Currently the gateway silently matches intents to skills via SkillBinder. The agent never knows what skills exist or which one was used. This spec makes skills a first-class citizen of the collaborative gateway pattern:

1. **Agent can list** available skills (mode `list`)
2. **Gateway suggests** matching skill in plan responses
3. **Agent can deliberately invoke** a specific skill (new `skill` parameter)

## 2. Design

### 2.1 New mode: `list`

```
dummie_process(intent="list", mode="list")
  → returns JSON array of all skill templates:
    { "skill_id": "tdd", "name": "Test-Driven Development", 
      "description": "...", "trigger_patterns": [...], "steps": 3 }
```

### 2.2 Skill suggestion in plan responses

When mode is `plan` or `auto` (with low confidence showing plan), and SkillBinder finds a match, include:

```json
{
  "plan": [...],
  "suggested_skill": "tdd",
  "skill_name": "Test-Driven Development",
  "skill_description": "Find tests, run them, and implement missing functionality."
}
```

### 2.3 Deliberate skill invocation

New optional parameter `skill` on dummie_process:

```
dummie_process(intent="run tests on user model", skill="tdd")
  → skips SmartRouter classification
  → loads skill template directly
  → executes DAG
  → returns compact result
```

When `skill` is provided with `mode="plan"`:
- Shows the skill's step-by-step DAG without executing

When `skill` is provided with `mode="confirm"`:
- Executes the skill's DAG

## 3. Implementation

### 3.1 tools.py changes

Add `mode="list"` handling in dummie_process:

```python
async def dummie_process(intent: str, mode: str = "auto", 
                         skill: str = None,
                         plan: Optional[List[dict]] = None, ...) -> str:
    # NEW: list skills
    if mode == "list":
        return await self._handle_list()

    # NEW: force skill invocation
    if skill:
        return await self._handle_skill_invoke(intent, skill, mode)

    # existing flow...
```

### 3.2 skill_executor.py changes

Add `list_all()` method to SkillExecutor:

```python
def list_all(self) -> list[dict]:
    """Return all available skills as dicts."""
    return [
        {
            "skill_id": s.skill_id,
            "name": s.name,
            "description": s.description,
            "trigger_patterns": s.trigger_patterns,
            "step_count": len(s.steps),
        }
        for s in BUILTIN_SKILLS
    ]
```

### 3.3 Response format changes

In plan mode responses, add `suggested_skill` field when SkillBinder.match() succeeds.

## 4. Agent experience

Before:
```
Agent: "I need to run TDD on the user module"
Gateway: [silently matches TDD skill, executes 3 steps, returns pass/fail]
Agent: [has no idea a skill was used]
```

After:
```
Agent: dummie_process(intent="list", mode="list")
Gateway: ["tdd: Test-Driven Development...", "code_review: ...", ...]

Agent: dummie_process(intent="run tdd on user module", mode="plan")
Gateway: {plan: [...], suggested_skill: "tdd", skill_name: "Test-Driven Development"}

Agent: dummie_process(intent="run tdd on user module", mode="confirm", skill="tdd")
Gateway: [executes TDD DAG] → {status: "pass", coverage: "87%"}
```

## 5. Success criteria

- `mode="list"` returns all 4 built-in skills with descriptions
- Plan responses include `suggested_skill` when SkillBinder matches
- `skill="tdd"` parameter forces skill execution, skipping SmartRouter
- 38 SMART tests still pass
- Backward compatible (all existing modes work unchanged)