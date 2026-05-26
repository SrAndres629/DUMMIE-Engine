#!/usr/bin/env python3
"""Heartbeat Signal Generator — visible status indicator for Jorge.

Creates a human-readable signal file showing:
- Whether autonomous heartbeat mode is active
- How long it's been running
- What the last heartbeat did and thought
- Current blockers and warnings

Source of Truth: .aiwg/heartbeat/latest_heartbeat.json
Output: .aiwg/heartbeat/signal.json + HEARTBEAT.md
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

HB_DIR = Path("/opt/dummie-engine/.aiwg/heartbeat")
LATEST_HB = HB_DIR / "latest_heartbeat.json"
SIGNAL_FILE = HB_DIR / "signal.json"
HEARTBEAT_MD = Path("/opt/dummie-engine/HEARTBEAT.md")
INDEX_FILE = HB_DIR / "heartbeat_index.json"
LEDGER_FILE = HB_DIR / "heartbeat_ledger.jsonl"


def load_latest_heartbeat() -> dict:
    if not LATEST_HB.exists():
        return None
    with open(LATEST_HB) as f:
        return json.load(f)


def count_heartbeats() -> int:
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE) as f:
            return sum(1 for _ in f)
    return 0


def get_last_timestamp(hb: dict) -> str:
    return hb.get("created_at", "unknown")


def generate_signal(hb: dict) -> dict:
    if not hb:
        return {
            "status": "NO_HEARTBEAT",
            "message": "No heartbeat has been executed yet",
            "mode": "unknown",
            "decision": "unknown",
            "last_run": "never",
            "total_heartbeats": 0,
            "active_blockers": [],
            "warnings": [],
            "what_did": "N/A",
            "what_thought": "N/A",
        }

    obs = hb.get("observation", {})
    whole_body = obs.get("whole_body_scan", {})
    decision = hb.get("decision", "UNKNOWN")
    mode = hb.get("mode", "unknown")
    created = get_last_timestamp(hb)

    # Determine operational status
    blockers = obs.get("active_blockers", [])
    kuzu_degraded = obs.get("kuzu_degraded", False)
    coherence = whole_body.get("overall_coherence_score", 0)

    if decision == "PASS_WITH_WARNINGS":
        status = "OPERATIONAL_WITH_WARNINGS"
    elif decision == "PASS":
        status = "HEALTHY"
    elif decision == "FAIL":
        status = "DEGRADED"
    else:
        status = "NEEDS_ATTENTION"

    # What did the heartbeat do?
    steps_executed = []
    if obs.get("git_clean") is not None:
        steps_executed.append("Git state verified")
    if obs.get("canonical_inputs") is not None:
        steps_executed.append(f"Loaded {len(obs['canonical_inputs'])} canonical inputs")
    if obs.get("missing_inputs"):
        steps_executed.append(f"Found {len(obs['missing_inputs'])} missing inputs")
    if hb.get("truth_hygiene"):
        steps_executed.append("Truth hygiene scan completed")
    if hb.get("epistemic_state"):
        steps_executed.append("Epistemic state built")
    if hb.get("bias_report"):
        steps_executed.append("Cognitive bias scan completed")
    if hb.get("mental_model"):
        steps_executed.append("Mental model loop executed")
    if hb.get("self_improvement_queue"):
        steps_executed.append("Self-improvement queue loaded")

    # What did the heartbeat think?
    thoughts = []
    if whole_body:
        thoughts.append(f"Coherence score: {coherence:.1f}%")
        thoughts.append(f"Active modules: {whole_body.get('active_modules', 0)}")
        thoughts.append(f"Shadow modules: {whole_body.get('shadow_modules', 0)}")
    if hb.get("warnings"):
        for w in hb["warnings"]:
            thoughts.append(f"WARNING: {w}")
    if hb.get("degraded_capabilities"):
        thoughts.append(f"Degraded capabilities: {len(hb['degraded_capabilities'])}")
    if hb.get("dispatch_recommendation"):
        thoughts.append(f"Dispatch: {hb['dispatch_recommendation']}")
    if hb.get("selected_action"):
        thoughts.append(f"Selected action: {hb['selected_action']}")

    # Calculate time since last heartbeat
    time_since = "unknown"
    try:
        last_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        now = datetime.now(last_dt.tzinfo)
        delta = now - last_dt
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        time_since = f"{hours}h {minutes}m ago"
    except Exception:
        pass

    return {
        "status": status,
        "mode": mode,
        "decision": decision,
        "last_run": created,
        "time_since": time_since,
        "total_heartbeats": count_heartbeats(),
        "coherence_score": coherence,
        "active_blockers": blockers,
        "kuzu_degraded": kuzu_degraded,
        "warnings": hb.get("warnings", []),
        "what_did": steps_executed,
        "what_thought": thoughts,
        "dispatch_recommendation": hb.get("dispatch_recommendation", "N/A"),
        "selected_action": hb.get("selected_action", "N/A"),
        "degraded_capabilities_count": len(hb.get("degraded_capabilities", [])),
    }


def update_heartbeat_md(signal: dict):
    """Update HEARTBEAT.md with current status."""
    status_icon = {
        "HEALTHY": "✅",
        "OPERATIONAL_WITH_WARNINGS": "⚠️",
        "DEGRADED": "❌",
        "NEEDS_ATTENTION": "🔴",
        "NO_HEARTBEAT": "⏸️",
    }.get(signal["status"], "❓")

    blockers_text = "None"
    if signal["active_blockers"]:
        blockers_text = ", ".join(signal["active_blockers"])

    last_run = signal["last_run"]
    if last_run != "unknown":
        try:
            dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            last_run = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            pass

    content = f"""# L0 Autonomous Heartbeat

{status_icon} **Status:** {signal["status"]}
{status_icon} **Mode:** {signal["mode"]}
{status_icon} **Decision:** {signal["decision"]}
{status_icon} **Last Run:** {last_run} ({signal["time_since"]})
{status_icon} **Total Heartbeats:** {signal["total_heartbeats"]}
{status_icon} **Coherence Score:** {signal.get("coherence_score", 0):.1f}%

## Active Blockers
{blockers_text}

## Last Cycle Summary
- **What it did:** {"; ".join(signal["what_did"][:5])}
- **What it thought:** {"; ".join(signal["what_thought"][:5])}
- **Dispatch:** {signal["dispatch_recommendation"]}
- **Selected Action:** {signal["selected_action"]}
- **Degraded Capabilities:** {signal["degraded_capabilities_count"]}

## Warnings
"""
    if signal["warnings"]:
        for w in signal["warnings"]:
            content += f"- {w}\n"
    else:
        content += "None\n"

    content += f"\n---\n*Updated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}*\n"

    HEARTBEAT_MD.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_MD.write_text(content)


def main():
    hb = load_latest_heartbeat()
    signal = generate_signal(hb)

    # Write signal JSON
    SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SIGNAL_FILE, "w") as f:
        json.dump(signal, f, indent=2, default=str)

    # Update HEARTBEAT.md
    update_heartbeat_md(signal)

    # Print to stdout
    print(json.dumps(signal, indent=2, default=str))


if __name__ == "__main__":
    main()
