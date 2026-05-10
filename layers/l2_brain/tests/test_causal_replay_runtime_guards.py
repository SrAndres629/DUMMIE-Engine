import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from causal_replay import CausalEvent, replay_until
from runtime_guards import GuardInput, evaluate_runtime_guards


def test_causal_replay_reconstructs_frame_at_lamport_tick():
    events = [
        CausalEvent(
            event_id="ev-1",
            lamport_t=1,
            causal_hash="h1",
            parent_hashes=["GENESIS"],
            context={"spec": "A"},
        ),
        CausalEvent(
            event_id="ev-2",
            lamport_t=2,
            causal_hash="h2",
            parent_hashes=["h1"],
            context={"decision": "B"},
        ),
    ]

    frame = replay_until(events, target_lamport_t=2)

    assert frame.head_hash == "h2"
    assert frame.context["spec"] == "A"
    assert frame.context["decision"] == "B"


def test_runtime_guards_block_unready_provider_and_missing_spec():
    result = evaluate_runtime_guards(
        GuardInput(
            provider_ready=False,
            memory_locked=False,
            parent_spec_approved=False,
            l3_policy="ALLOWED",
        )
    )

    assert result.status == "BLOCK"
    assert "provider_not_ready" in result.reasons
    assert "parent_spec_not_approved" in result.reasons


def test_runtime_guards_require_intervention_for_l3_policy():
    result = evaluate_runtime_guards(
        GuardInput(
            provider_ready=True,
            memory_locked=False,
            parent_spec_approved=True,
            l3_policy="L3_INTERVENTION_REQUIRED",
        )
    )

    assert result.status == "REVIEW"
