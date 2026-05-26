---
status: SUPERSEDED
claims:
- id: compression_module
  description: result_compression.py importable y funcional
  severity: critical
- id: compression_integrated
  description: compress_result integrado en dummie_process
  severity: high
implementations:
- file: layers/l1_nervous/result_compression.py
  class: ResultCompressor
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Gateway-Side Result Compression

**Date:** 2026-05-26
**Phase:** G4
**Requires reboot:** No
**Depends on:** Nothing
**Files modified:** `layers/l1_nervous/tools.py` (add _compact_result, use in dummie_process)

## Problem

Tool outputs are returned raw to the agent. A `search_files` returns full JSON with file paths, sizes, timestamps. An `execute_command` returns stdout + stderr + exit code. This raw data accumulates in context, consuming thousands of tokens across a session.

The agent only needs the **signal**, not the **noise**.

## Design

### Compression function

```python
def _compact_result(tool_name: str, raw: str, max_chars: int = 500) -> str:
    """Compress raw tool output to essential information for the agent."""
    if not raw:
        return "(empty result)"
    
    # Already compact? Return as-is
    if len(raw) <= max_chars:
        return raw
    
    raw_lower = tool_name.lower()
    
    # Search tools: return file list only, not metadata
    if any(kw in raw_lower for kw in ("search", "find", "glob", "list", "ls")):
        lines = raw.split("\n")
        paths = [l.strip() for l in lines if l.strip() and not l.strip().startswith("{")]
        count = len(paths)
        preview = "\n".join(paths[:10])
        return f"[{count} results]\n{preview}" + (
            f"\n... and {count - 10} more" if count > 10 else ""
        )
    
    # Read tools: first N chars + length indicator
    if any(kw in raw_lower for kw in ("read", "cat", "get", "show")):
        return raw[:max_chars] + f"\n... (total: {len(raw)} chars)"
    
    # Execute/shell: exit code + errors only
    if any(kw in raw_lower for kw in ("exec", "run", "cmd", "bash", "shell")):
        # Try to extract exit code and errors
        lines = raw.split("\n")
        errors = [l for l in lines if "error" in l.lower() or "fail" in l.lower()]
        return (
            f"[output: {len(raw)} chars]"
            + (f"\nErrors:\n" + "\n".join(errors[:5]) if errors else "")
        )
    
    # Status/diff/log: truncated
    if any(kw in raw_lower for kw in ("status", "diff", "log", "history")):
        return raw[:max_chars] + f"\n... (truncated from {len(raw)} chars)"
    
    # Default: truncate
    return raw[:max_chars] + f"\n... (truncated from {len(raw)} chars)"
```

### Integration in dummie_process

The execution section (step 6) already does `str(exec_result)[:1000]`. Replace with:

```python
# ── 6. Execute ──
if route_info.get("match") and mode in ("execute", "auto") and smart_used:
    tools = route_info.get("tools", [])
    if tools and tools[0]:
        try:
            exec_result = await proxy_mgr.call_tool(
                tools[0]["server"],
                tools[0]["tool"],
                tools[0].get("arguments", {}),
            )
            raw_str = str(exec_result)
            execution["executed"] = True
            execution["result"] = _compact_result(tools[0]["tool"], raw_str)
            execution["raw_length"] = len(raw_str)
        except Exception as e:
            execution["error"] = str(e)
```

The agent sees `result` (compact) and `raw_length` (metadata), giving it the option to request the full output if needed.

### Compression in skill execution

SkillExecutor already truncates to 500 chars in `_execute_step()`. Add `_compact_result` call:

```python
async def _execute_step(self, step, intent):
    result = await self.proxy.call_tool(step.server, step.tool, args)
    raw = str(result)
    self._results[step.step_id] = {
        "success": True,
        "output": _compact_result(step.tool, raw),
        "raw_length": len(raw),
        "step_description": step.description,
    }
```

## Success criteria

| Metric | Before | After |
|--------|--------|-------|
| search_files output | Full JSON (500+ chars) | File names + count (~100 chars) |
| read_file output | Full content (2000+ chars) | First 500 chars + total |
| execute_command output | stdout + stderr + exit | Exit info + errors only |
| Skill DAG output | Raw per step | Compact per step |
| Agent context waste per tool call | ~80% raw noise | ~20% metadata |