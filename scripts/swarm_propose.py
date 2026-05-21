#!/usr/bin/env python3
"""swarm_propose.py — Propose a new pack and auto-merge when 2/3 consensus reached."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEBATE_DIR = os.path.join(PROJECT_ROOT, ".aiwg", "agent_mesh", "debate")
PROPOSALS_DIR = os.path.join(DEBATE_DIR, "proposals")
OUTBOX_DIR = os.path.join(DEBATE_DIR, "outbox")
BACKLOG_PATH = os.path.join(DEBATE_DIR, "backlog.json")

WORKER_INBOX = os.path.join(OUTBOX_DIR, "worker_inbox.jsonl")
REVIEWER_INBOX = os.path.join(OUTBOX_DIR, "reviewer_inbox.jsonl")

VOTING_AGENTS = ["worker", "reviewer", "supervisor"]
QUORUM = len(VOTING_AGENTS)
QUORUM_THRESHOLD = 2  # 2/3 majority


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def append_jsonl(path, entry):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def create_proposal(pack_name, name, rationale, priority, proposed_by):
    pfile = os.path.join(PROPOSALS_DIR, f"{pack_name}.json")
    existing = load_json(pfile)
    if existing:
        print(
            f"[{timestamp()}] WARN: Proposal for {pack_name} already exists — updating"
        )
        existing["rationale"] = rationale
        existing["priority"] = priority
        existing["updated_at"] = timestamp()
        data = existing
    else:
        data = {
            "pack": pack_name,
            "name": name,
            "rationale": rationale,
            "priority": priority,
            "proposed_by": proposed_by,
            "proposed_at": timestamp(),
            "votes": {agent: None for agent in VOTING_AGENTS},
            "status": "pending_votes",
            "updated_at": timestamp(),
        }
    write_json(pfile, data)
    return data


def check_proposals_for_merge():
    if not os.path.isdir(PROPOSALS_DIR):
        return

    proposal_files = sorted(f for f in os.listdir(PROPOSALS_DIR) if f.endswith(".json"))

    for pf in proposal_files:
        pfile = os.path.join(PROPOSALS_DIR, pf)
        proposal = load_json(pfile)
        if proposal is None or proposal.get("status") != "pending_votes":
            continue

        votes = proposal.get("votes", {})
        approvals = sum(1 for v in votes.values() if v is True)
        rejections = sum(1 for v in votes.values() if v is False)

        if approvals >= QUORUM_THRESHOLD:
            proposal["status"] = "approved"
            proposal["updated_at"] = timestamp()
            write_json(pfile, proposal)
            merge_proposal_to_backlog(proposal)
            notify_proposal_approved(proposal)
        elif rejections >= QUORUM_THRESHOLD:
            proposal["status"] = "rejected"
            proposal["updated_at"] = timestamp()
            write_json(pfile, proposal)


def merge_proposal_to_backlog(proposal):
    backlog = load_json(BACKLOG_PATH)
    if backlog is None:
        backlog = {"schema": "dummie.swarm.backlog.v1", "backlog": []}

    for entry in backlog.get("backlog", []):
        if entry.get("pack") == proposal["pack"]:
            print(f"[{timestamp()}] SKIP: {proposal['pack']} already in backlog")
            return

    new_entry = {
        "pack": proposal["pack"],
        "name": proposal["name"],
        "rationale": proposal["rationale"],
        "status": "pending",
        "priority": proposal.get("priority", "medium"),
        "prerequisites": [],
        "verification": [],
        "merged_from_proposal": True,
        "merged_at": timestamp(),
    }

    backlog.setdefault("backlog", []).append(new_entry)
    write_json(BACKLOG_PATH, backlog)
    print(f"[{timestamp()}] MERGED: {proposal['pack']} added to backlog")


def notify_proposal(proposal):
    entry = {
        "timestamp": timestamp(),
        "type": "new_proposal",
        "pack": proposal["pack"],
        "name": proposal["name"],
        "rationale": proposal["rationale"],
        "priority": proposal.get("priority", "medium"),
        "proposed_by": proposal["proposed_by"],
    }
    append_jsonl(WORKER_INBOX, entry)
    append_jsonl(REVIEWER_INBOX, entry)


def notify_proposal_approved(proposal):
    entry = {
        "timestamp": timestamp(),
        "type": "proposal_approved",
        "pack": proposal["pack"],
        "name": proposal["name"],
    }
    append_jsonl(WORKER_INBOX, entry)
    append_jsonl(REVIEWER_INBOX, entry)


def main():
    parser = argparse.ArgumentParser(description="DUMMIE Swarm — Propose New Pack")
    parser.add_argument("--pack", required=True, help="Pack identifier")
    parser.add_argument("--name", required=True, help="Human-readable pack name")
    parser.add_argument("--rationale", required=True, help="Why this pack is needed")
    parser.add_argument(
        "--priority",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Pack priority",
    )
    parser.add_argument(
        "--proposed-by",
        required=True,
        help="Who is proposing (worker|reviewer|supervisor)",
    )
    args = parser.parse_args()

    print(f"[{timestamp()}] PROPOSE: {args.pack} — {args.name}")

    proposal = create_proposal(
        args.pack, args.name, args.rationale, args.priority, args.proposed_by
    )
    print(f"[{timestamp()}] OK: proposals/{args.pack}.json created")
    print(f"[{timestamp()}] INFO: Votes: {proposal['votes']}")

    notify_proposal(proposal)
    print(f"[{timestamp()}] OK: outbox — agents notified of new proposal")

    check_proposals_for_merge()
    print(
        f"[{timestamp()}] OK: checked all proposals for consensus (2/{QUORUM} threshold)"
    )

    print(f"[{timestamp()}] PROPOSE: {args.pack} — done")


if __name__ == "__main__":
    main()
