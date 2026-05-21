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
    parser.add_argument("--evidence-dir", default=None)
    args = parser.parse_args()
    os.chdir(Path(__file__).resolve().parent.parent)
    cons_file = CONSENSUS_DIR / f"{args.pack}.json"
    consensus = {"pack": args.pack, "worker_vote": True, "reviewer_vote": False, "deadlock": False}
    if cons_file.exists():
        try:
            existing = json.loads(cons_file.read_text())
            existing["worker_vote"] = True
            consensus = existing
        except: pass
    cons_file.write_text(json.dumps(consensus, indent=2) + "\n")
    print(f"CONSENSUS_WRITTEN:{cons_file}")
    evidence_dir = args.evidence_dir or f"evidence/{args.pack}"
    msg = {"timestamp": datetime.now(timezone.utc).isoformat(), "pack": args.pack, "status": "ready_for_review", "evidence_dir": evidence_dir, "worker_vote": True}
    outbox_file = OUTBOX / "reviewer_inbox.jsonl"
    messages = []
    if outbox_file.exists():
        text = outbox_file.read_text().strip()
        if text:
            messages = [json.loads(line) for line in text.split("\n") if line.strip()]
    messages.append(msg)
    outbox_file.write_text("\n".join(json.dumps(m) for m in messages) + "\n")
    print(f"REVIEWER_NOTIFIED:{args.pack}")

if __name__ == "__main__":
    main()
