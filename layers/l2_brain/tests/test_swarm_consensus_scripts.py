import scripts.swarm_ack as swarm_ack


def test_swarm_ack_initial_consensus_leaves_reviewer_unvoted():
    consensus = swarm_ack.build_initial_consensus("PACK_X")

    assert consensus == {
        "pack": "PACK_X",
        "worker_vote": True,
        "reviewer_vote": None,
        "deadlock": False,
    }


def test_swarm_ack_resets_reviewer_rejection_to_pending_on_new_worker_ack():
    consensus = swarm_ack.apply_worker_ack(
        {
            "pack": "PACK_X",
            "worker_vote": True,
            "reviewer_vote": False,
            "deadlock": True,
        }
    )

    assert consensus["worker_vote"] is True
    assert consensus["reviewer_vote"] is None
    assert consensus["deadlock"] is False
