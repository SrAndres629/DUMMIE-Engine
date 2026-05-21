#!/usr/bin/env python3
import argparse, json, os
from datetime import datetime, timezone
from pathlib import Path

MESH = Path(".aiwg/agent_mesh/debate")
CONSENSUS_DIR = MESH / "consensus"
OUTBOX = MESH / "outbox"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--approve", action="store_true")
    group.add_argument("--reject", action="store_true")
    parser.add_argument("--feedback", default=None)
    args = parser.parse_args()
    os.chdir(Path(__file__).resolve().parent.parent)
    cons_file = CONSENSUS_DIR / f"{args.pack}.json"
    consensus = {"pack": args.pack, "worker_vote": False, "reviewer_vote": True, "deadlock": False}
    if cons_file.exists():
        try:
            existing = json.loads(cons_file.read_text())
            existing["reviewer_vote"] = True
            consensus = existing
        except: pass
    if args.reject:
        consensus["reviewer_vote"] = False
        consensus["deadlock_rounds"] = consensus.get("deadlock_rounds", 0) + 1
        if consensus["deadlock_rounds"] >= 3: consensus["deadlock"] = True
    cons_file.write_text(json.dumps(consensus, indent=2) + "\n")
    print(f"CONSENSUS_WRITTEN:{cons_file}")
    if args.reject and args.feedback:
        msg = {"timestamp": datetime.now(timezone.utc).isoformat(), "pack": args.pack, "feedback": args.feedback}
        outbox_file = OUTBOX / "worker_inbox.jsonl"
        messages = []
        if outbox_file.exists():
            text = outbox_file.read_text().strip()
            if text:
                messages = [json.loads(line) for line in text.split("\n") if line.strip()]
        messages.append(msg)
        outbox_file.write_text("\n".join(json.dumps(m) for m in messages) + "\n")
        print(f"FEEDBACK_SENT:{args.pack}")
    if consensus.get("deadlock"):
        print(f"DEADLOCK:{args.pack}")

if __name__ == "__main__":
    main()
