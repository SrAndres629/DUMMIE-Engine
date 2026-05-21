#!/usr/bin/env python3
"""swarm_check.py — Check swarm status from backlog and consensus."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEBATE_DIR = os.path.join(PROJECT_ROOT, ".aiwg", "agent_mesh", "debate")
CONSENSUS_DIR = os.path.join(DEBATE_DIR, "consensus")
BACKLOG_PATH = os.path.join(DEBATE_DIR, "backlog.json")

ROLE_VOTE_KEYS = {
    "worker": "worker_vote",
    "reviewer": "reviewer_vote",
    "supervisor": None,
}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main():
    parser = argparse.ArgumentParser(description="DUMMIE Swarm Status Check")
    parser.add_argument(
        "--role", default=None, help="Filter by agent role (worker|reviewer|supervisor)"
    )
    args = parser.parse_args()

    backlog = load_json(BACKLOG_PATH)
    if backlog is None:
        print(f"[{timestamp()}] SWARM_STATUS: ERROR — cannot read backlog.json")
        sys.exit(1)

    all_packs = backlog.get("backlog", [])
    total = len(all_packs)
    completed = sum(1 for p in all_packs if p.get("status") == "completed")
    pending = sum(1 for p in all_packs if p.get("status") == "pending")

    print(
        f"[{timestamp()}] SWARM_STATUS: {completed}/{total} completed ({pending} pending)"
    )
    print()

    if not os.path.isdir(CONSENSUS_DIR):
        print(f"[{timestamp()}] SWARM_STATUS: No consensus directory found")
        sys.exit(0)

    consensus_files = sorted(
        f
        for f in os.listdir(CONSENSUS_DIR)
        if f.endswith(".json") and f != "current.json"
    )
    print(f"[{timestamp()}] Consensus files: {len(consensus_files)}")
    print()

    vote_key = ROLE_VOTE_KEYS.get(args.role) if args.role else None

    for cf in consensus_files:
        cpath = os.path.join(CONSENSUS_DIR, cf)
        data = load_json(cpath)
        if data is None:
            print(f"  {cf}: <unreadable>")
            continue
        pack_name = data.get("pack", cf.replace(".json", ""))
        worker = data.get("worker_vote", "—")
        reviewer = data.get("reviewer_vote", "—")
        deadlock = data.get("deadlock", False)
        deadlock_flag = " [DEADLOCK]" if deadlock else ""

        if vote_key:
            vote = data.get(vote_key, "—")
            status = (
                "voted"
                if vote is True
                else ("rejected" if vote is False else "not voted")
            )
            match = "<<" if vote is True else ""
            print(f"  {pack_name}: {args.role}={vote} {status} {match}")
        else:
            print(f"  {pack_name}: worker={worker}, reviewer={reviewer}{deadlock_flag}")

    print()
    print(f"[{timestamp()}] SWARM_STATUS: check complete")


if __name__ == "__main__":
    main()
