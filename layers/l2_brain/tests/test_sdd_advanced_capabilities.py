import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from branch_memory import BranchMemory, promote_merge_summary
from formal_bridge import FormalModel, verify_formal_model
from golden_path import generate_golden_path
from human_intent import classify_human_artifact
from nervous_pulse import SpecEvolution, WorkSubscription, compute_stale_agent_pulses
from self_optimization import FailureSignal, propose_self_optimization
from semantic_graph_rag import GraphFact, answer_why_decision
from witness import WitnessNode, validate_witness_chain


def test_nervous_pulse_interrupts_agents_with_stale_spec_dependency():
    pulses = compute_stale_agent_pulses(
        evolutions=[
            SpecEvolution(spec_id="spec-1", old_hash="a", new_hash="b", lamport_t=7)
        ],
        subscriptions=[
            WorkSubscription(agent_id="agent-1", workroom_id="wr-1", spec_id="spec-1", seen_hash="a"),
            WorkSubscription(agent_id="agent-2", workroom_id="wr-2", spec_id="spec-1", seen_hash="b"),
        ],
    )

    assert len(pulses) == 1
    assert pulses[0].agent_id == "agent-1"
    assert pulses[0].severity == "INTERRUPT"


def test_semantic_graph_rag_answers_decision_rationale():
    answer = answer_why_decision(
        "Why Arrow IPC?",
        [
            GraphFact(kind="decision", subject="Arrow IPC", predicate="chosen_over", object="Protocol Buffers"),
            GraphFact(kind="rationale", subject="Arrow IPC", predicate="because", object="zero-copy memory plane"),
        ],
    )

    assert "zero-copy memory plane" in answer.text
    assert answer.evidence_refs == ["Arrow IPC:because"]


def test_witness_validates_contiguous_causal_chain():
    result = validate_witness_chain(
        [
            WitnessNode(causal_hash="h1", parent_hashes=["GENESIS"], lamport_t=1),
            WitnessNode(causal_hash="h2", parent_hashes=["h1"], lamport_t=2),
        ]
    )

    assert result.status == "VALID"


def test_witness_rejects_broken_parent_link():
    result = validate_witness_chain(
        [
            WitnessNode(causal_hash="h1", parent_hashes=["GENESIS"], lamport_t=1),
            WitnessNode(causal_hash="h2", parent_hashes=["wrong"], lamport_t=2),
        ]
    )

    assert result.status == "INVALID"
    assert "parent_hashes" in result.reason


def test_self_optimization_proposes_spec_refactor_for_repeated_failures():
    proposal = propose_self_optimization(
        [
            FailureSignal(locus="layers/l1_nervous/mcp_proxy.py", category="protocol_failure"),
            FailureSignal(locus="layers/l1_nervous/mcp_proxy.py", category="protocol_failure"),
            FailureSignal(locus="layers/l1_nervous/mcp_proxy.py", category="protocol_failure"),
        ],
        threshold=3,
    )

    assert proposal is not None
    assert proposal.target_locus == "layers/l1_nervous/mcp_proxy.py"
    assert proposal.proposed_action == "SPEC_REFACTOR"


def test_formal_bridge_accepts_model_without_forbidden_states():
    result = verify_formal_model(
        FormalModel(
            model_id="mcp-handshake",
            invariants=["eventually READY", "no tools/call before READY"],
            forbidden_states=[],
        )
    )

    assert result.status == "PROVEN"


def test_golden_path_generates_tests_interfaces_and_docs_from_spec():
    path = generate_golden_path(
        spec_id="sdd",
        approved=True,
        target_module="layers/l2_brain/sdd_governance.py",
    )

    assert path.allowed is True
    assert "tests" in path.steps[0].lower()
    assert path.parent_spec_id == "sdd"


def test_human_intent_classifier_distinguishes_decision_from_idea():
    decision = classify_human_artifact("# Decision\nWe will use append-only journals.")
    idea = classify_human_artifact("# Idea\nMaybe we could rewrite everything.")

    assert decision.kind == "decision"
    assert decision.authority == "HIGH"
    assert idea.kind == "idea"
    assert idea.authority == "LOW"


def test_branch_memory_promotes_only_relevant_merge_summary():
    branch = BranchMemory(
        branch_id="feature/sdd",
        decisions=["Use admission control"],
        failures=["Missing parent spec"],
        transient_notes=["temporary print debugging"],
    )

    summary = promote_merge_summary(branch)

    assert "Use admission control" in summary.promoted_items
    assert "temporary print debugging" not in summary.promoted_items
