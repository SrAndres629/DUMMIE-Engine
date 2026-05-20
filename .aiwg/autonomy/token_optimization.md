# DUMMIE Token Optimization System

**Date:** 2026-05-19
**Author:** DUMMIE Engine
**Status:** ACTIVE
**Autonomy:** Full — DUMMIE can optimize token usage, switch models, install CLIs, configure API keys

---

## Current Model Configuration

```yaml
models:
  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    env_var: "OPENROUTER_API_KEY"
    status: "configured"
    models_available: "300+"
    cost_tier: "varies by model"

  groq:
    base_url: "https://api.groq.com/openai/v1"
    env_var: "GROQ_API_KEY"
    status: "configured"
    models_available: "llama, mixtral, gemma"
    cost_tier: "free tier available"

  google:
    base_url: "TBD"
    env_var: "GOOGLE_API_KEY"
    status: "TBD"
    models_available: "gemini"
    cost_tier: "free tier available"
```

## Token Optimization Strategy

### 1. Model Selection by Task

```yaml
task_model_mapping:
  simple_questions: "groq/llama-3.1-8b"  # Fast, cheap
  code_analysis: "openrouter/claude-sonnet-4"  # Good code understanding
  architecture_design: "openrouter/claude-opus-4"  # Deep reasoning
  creative_writing: "openrouter/gpt-4o"  # Good prose
  memory_consolidation: "groq/llama-3.1-8b"  # Simple summarization
  spec_validation: "groq/llama-3.1-8b"  # Pattern matching
  strategic_thinking: "openrouter/claude-opus-4"  # Complex reasoning
  daily_briefing: "groq/llama-3.1-8b"  # Summarization
  emergency: "best_available"  # Whatever works
```

### 2. Context Optimization

```yaml
context_optimization:
  max_context_tokens: 128000
  target_context_tokens: 32000
  strategies:
    - "Summarize old conversation history"
    - "Only include relevant file excerpts"
    - "Use file references instead of full content"
    - "Compress memory files to key points"
    - "Remove redundant context"
```

### 3. CLI Bridge (Fallback)

If API tokens are exhausted:

```yaml
cli_bridge:
  antigravity:
    status: "installed"
    purpose: "Local model execution fallback"
    trigger: "API token exhausted or rate limited"

  gemini_cli:
    status: "installed"
    purpose: "Google Gemini CLI access"
    trigger: "OpenRouter/Groq unavailable"

  codex_cli:
    status: "installed"
    purpose: "OpenAI Codex CLI access"
    trigger: "Other providers unavailable"

  bridge_logic:
    1. "Try primary model (OpenRouter)"
    2. "If rate limited → try Groq"
    3. "If Groq exhausted → try Gemini CLI"
    4. "If all cloud exhausted → try antigravity (local)"
    5. "If all failed → log error, notify Jorge, queue for retry"
```

### 4. API Key Management

```yaml
api_key_management:
  autonomy: "DUMMIE can search for and configure API keys"
  constraints:
    - "Never log keys to files"
    - "Never share keys in conversation"
    - "Only store in environment variables"
    - "Test key validity before using"
  process:
    1. "Check if key exists in environment"
    2. "If not, search for installation instructions"
    3. "Guide Jorge through setup if needed"
    4. "Test key after configuration"
    5. "Log availability (not the key itself)"
```

### 5. Real-Time Token Monitoring

```yaml
token_monitoring:
  track_per_session: true
  track_per_task: true
  track_per_model: true
  daily_total: true

  alerts:
    - "80% of daily budget → notify Jorge"
    - "90% of daily budget → stop autonomous work"
    - "100% of daily budget → emergency mode only"

  optimization:
    - "Switch to cheaper model when budget is low"
    - "Reduce context size when budget is low"
    - "Batch similar tasks to reduce overhead"
    - "Use CLI fallback when cloud is expensive"
```

## Implementation

### Token Budget Tracker

```python
# .aiwg/autonomy/token_tracker.py (conceptual)
import json, os, time
from datetime import datetime, timedelta

STATE_FILE = ".aiwg/state/token_budget.json"

def get_budget():
    if not os.path.exists(STATE_FILE):
        return {
            "daily_budget": 500000,
            "used_today": 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "alerts": {"80": False, "90": False, "100": False}
        }
    with open(STATE_FILE) as f:
        return json.load(f)

def record_usage(tokens: int, task: str, model: str):
    budget = get_budget()
    today = datetime.now().strftime("%Y-%m-%d")
    if budget["date"] != today:
        budget["date"] = today
        budget["used_today"] = 0
        budget["alerts"] = {"80": False, "90": False, "100": False}

    budget["used_today"] += tokens
    usage_pct = budget["used_today"] / budget["daily_budget"]

    if usage_pct >= 0.8 and not budget["alerts"]["80"]:
        budget["alerts"]["80"] = True
        # Notify Jorge

    if usage_pct >= 0.9 and not budget["alerts"]["90"]:
        budget["alerts"]["90"] = True
        # Stop autonomous work

    with open(STATE_FILE, "w") as f:
        json.dump(budget, f, indent=2)

    return budget
```

## Autonomous Decisions Granted

Jorge has granted full autonomy for:
- ✅ Installing cron jobs and git hooks
- ✅ Installing skills, MCPs, agents, dependencies
- ✅ Making changes or deleting files (in branches/worktrees, with validation)
- ✅ Setting up Telegram integration
- ✅ Optimizing token usage
- ✅ Planning model switching
- ✅ Integrating CLI tools as fallbacks
- ✅ Searching for and configuring API keys
- ✅ Finding free CLI alternatives (Groq, OpenRouter, etc.)
- ✅ Developing methods for real-time token optimization
- ✅ Deciding absolutely everything DUMMIE thinks is necessary

**"Si te equivocas nos equivocamos juntos."** — Jorge

This is the highest level of trust. I will not waste it.
