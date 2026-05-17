"""Tests for metacognitive_evolution_flywheel.py — Hardened Pack 5.2.2"""
from metacognitive_evolution_flywheel import run_metacognitive_evolution_flywheel


def test_flywheel_basic():
    res = run_metacognitive_evolution_flywheel("test intent", mode="observe_only")
    assert res.decision == "PASS"
    assert res.evolution_delta.get("next_check_recommended") != ""


def test_flywheel_full_mode():
    res = run_metacognitive_evolution_flywheel("test intent", mode="full")
    assert res.decision == "PASS"
    assert res.belief_revision != ""
