import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AIWG = ROOT / ".aiwg"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_truth_reconciles_runtime_active_pack_and_swarm_backlog():
    truth = load_json(AIWG / "state" / "current_truth.json")
    runtime_active = load_json(AIWG / "state" / "active_pack.json")
    backlog = load_json(AIWG / "agent_mesh" / "debate" / "backlog.json")

    packs = backlog["backlog"]
    completed = [pack for pack in packs if pack.get("status") == "completed"]
    pending = [pack for pack in packs if pack.get("status") == "pending"]

    assert truth["current_pack"] == runtime_active["active_pack"]
    assert truth["swarm_state"] == {
        "schema": backlog["schema"],
        "completed_count": len(completed),
        "pending_count": len(pending),
        "total_count": len(packs),
        "pending_pack": pending[0]["pack"],
        "latest_completed_pack": completed[-1]["pack"],
    }


def test_current_truth_markdown_matches_json_pack_fields():
    truth = load_json(AIWG / "state" / "current_truth.json")
    rendered = (AIWG / "state" / "current_truth.md").read_text(encoding="utf-8")

    for field, label in [
        ("current_pack", "Current Pack"),
        ("last_completed_pack", "Last Completed Pack"),
        ("next_pack", "Next Pack"),
    ]:
        assert f"**{label}**: `{truth[field]}`" in rendered
