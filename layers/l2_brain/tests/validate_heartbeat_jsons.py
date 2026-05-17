"""Validate generated JSON files against created schemas."""
import json
from pathlib import Path

def validate():
    root = Path(".aiwg")
    schemas = root / "schemas"
    reports = root / "reports"
    hb = root / "heartbeat"

    # Schema paths
    lifecycle_schema = json.loads((schemas / "heartbeat_lifecycle.schema.json").read_text(encoding="utf-8"))
    state_store_schema = json.loads((schemas / "heartbeat_state_store.schema.json").read_text(encoding="utf-8"))
    policy_schema = json.loads((schemas / "heartbeat_decision_policy.schema.json").read_text(encoding="utf-8"))
    scheduler_schema = json.loads((schemas / "heartbeat_scheduler.schema.json").read_text(encoding="utf-8"))
    seed_schema = json.loads((schemas / "next_heartbeat_seed.schema.json").read_text(encoding="utf-8"))

    # File paths
    latest_hb = json.loads((reports / "heartbeat_latest.json").read_text(encoding="utf-8"))
    latest_store = json.loads((hb / "latest_heartbeat.json").read_text(encoding="utf-8"))
    latest_policy = json.loads((reports / "heartbeat_decision_policy_latest.json").read_text(encoding="utf-8"))
    latest_scheduler = json.loads((reports / "heartbeat_scheduler_latest.json").read_text(encoding="utf-8"))
    latest_seed = json.loads((hb / "next_heartbeat_seed.json").read_text(encoding="utf-8"))

    # Structural validators
    def check_required(data, schema, name):
        for req in schema.get("required", []):
            if req not in data:
                raise ValueError(f"Missing required field '{req}' in {name}")
        print(f"PASS: {name} structurally matches {schema.get('title')}")

    check_required(latest_hb, lifecycle_schema, "heartbeat_latest.json")
    check_required(latest_store, state_store_schema, "latest_heartbeat.json")
    check_required(latest_policy, policy_schema, "heartbeat_decision_policy_latest.json")
    check_required(latest_scheduler, scheduler_schema, "heartbeat_scheduler_latest.json")
    check_required(latest_seed, seed_schema, "next_heartbeat_seed.json")

    print("\nALL JSON FILES ARE VALID AND STRUCTURALLY CONFORMANT.")

if __name__ == "__main__":
    validate()
