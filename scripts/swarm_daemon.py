#!/usr/bin/env python3
"""swarm_daemon.py — Autonomous swarm loop for DUMMIE debate workers."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEBATE_DIR = os.path.join(PROJECT_ROOT, ".aiwg", "agent_mesh", "debate")
AGENTS_DIR = os.path.join(PROJECT_ROOT, ".aiwg", "agent_mesh", "agents")
BACKLOG_PATH = os.path.join(DEBATE_DIR, "backlog.json")

ROLL_NAMES = {
    "worker": "opencode_worker",
    "reviewer": "opencode_reviewer",
    "supervisor": "opencode_supervisor",
}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def log(msg):
    print(f"[{timestamp()}] {msg}", flush=True)


def read_backlog():
    try:
        with open(BACKLOG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log(f"WARN: Cannot read backlog — {e}")
        return {"backlog": []}


def find_first_pending(backlog):
    for entry in backlog.get("backlog", []):
        if entry.get("status") == "pending":
            return entry
    return None


def read_targets(pack_name):
    path = os.path.join(DEBATE_DIR, f"{pack_name}_targets.txt")
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        log(f"WARN: Targets file not found for {pack_name} at {path}")
        return ""


def read_role_prompt(role_key):
    if not role_key:
        role_key = "worker"
    agent_dir_name = ROLL_NAMES.get(role_key, role_key) or "worker"
    prompt_path = os.path.join(AGENTS_DIR, agent_dir_name, "system_prompt.md")
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        log(f"WARN: No system_prompt.md for role '{role_key}' at {prompt_path}")
        return ""


def main():
    parser = argparse.ArgumentParser(description="DUMMIE Swarm Daemon")
    parser.add_argument(
        "--role", default="worker", help="Agent role (worker|reviewer|supervisor)"
    )
    args = parser.parse_args()

    role = args.role
    log(f"SWARM_DAEMON starting — role={role}")

    cycle = 0
    while True:
        cycle += 1
        log(f"--- Cycle {cycle} ---")

        role_prompt = read_role_prompt(role)
        if role_prompt:
            log(f"Role: {role}")
        else:
            log(f"Role: {role} (no prompt file)")

        backlog = read_backlog()
        pending = find_first_pending(backlog)

        if pending is None:
            log("STATUS: No pending packs — sleeping 15s")
            time.sleep(15)
            continue

        pack_name = pending["pack"]
        log(f"PACK: {pack_name} — {pending.get('name', '')}")

        targets = read_targets(pack_name)
        if targets:
            print(f"[{timestamp()}] TARGETS for {pack_name}:")
            print(targets)
        else:
            log(f"TASK: {pack_name} — no targets file, check backlog entry directly")
            print(json.dumps(pending, indent=2))

        log(f"Sleeping 15s...")
        time.sleep(15)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("SWARM_DAEMON shutting down")
        sys.exit(0)
