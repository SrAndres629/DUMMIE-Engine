# DUMMIE Session Chainer

**Purpose:** Automatically chain sessions when work remains
**State:** `.aiwg/state/session_*.json`
**Log:** `.aiwg/events/session_events.jsonl`

## Session State Schema

```json
{
  "session_id": "session_20260519_080000",
  "start_time": "2026-05-19T08:00:00Z",
  "end_time": "2026-05-19T10:30:00Z",
  "trigger": "task_001|jorge_message|cron|event",
  "objectives": ["Map L2 modules", "Identify dependencies"],
  "results": {
    "completed": ["Map L2 modules"],
    "pending": ["Identify dependencies"],
    "deliverables": [".aiwg/strategic/l2_module_inventory.json"]
  },
  "next_session": {
    "required": true,
    "objectives": ["Complete dependency mapping", "Catalog import paths"],
    "estimated_duration_hours": 1.5,
    "context_files": [".aiwg/strategic/l2_module_inventory.json"]
  },
  "token_usage": 45000,
  "errors": []
}
```

## Chaining Logic

```
Session ends
    ↓
Save session state to .aiwg/state/session_<id>.json
    ↓
Evaluate: is next_session.required?
    ↓ YES
    Check: is it quiet hours (23:00-06:00)?
    ↓ NO
    Check: is token budget exceeded?
    ↓ NO
    Check: was there progress last session?
    ↓ YES
    Generate next session prompt with:
      - Previous session results
      - Pending objectives
      - Context files to read
      - Task queue state
    ↓
    Schedule next session (via cron or daemon)
    ↓
    Log event to .aiwg/events/session_events.jsonl
    ↓
    Session ends (next session will trigger automatically)
```

## Quiet Hours

```yaml
quiet_hours:
  start: "23:00"
  end: "06:00"
  exceptions:
    - "critical alerts"
    - "jorge explicit request"
    - "security incidents"
```

## Token Budget

```yaml
daily_budget: 500000
allocation:
  heartbeat: 50000
  autonomous_tasks: 150000
  jorge_interactions: 200000
  emergency: 100000

alerts:
  80_percent: "Notify Jorge"
  90_percent: "Stop autonomous work"
  100_percent: "Emergency only"
```
