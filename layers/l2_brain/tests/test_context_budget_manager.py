import pytest
from layers.l2_brain.context_budget_manager import ContextBudgetManager

def test_context_budget_manager_allocate_budget():
    cbm = ContextBudgetManager()
    budget = cbm.allocate_budget("local_fast")
    assert budget["total_budget"] == 4096
    assert budget["compression_threshold"] == 3276

def test_context_budget_manager_should_compress():
    cbm = ContextBudgetManager()
    budget = cbm.allocate_budget("local_fast")
    
    packet_ok = {"items": [{"estimated_tokens": 1000}]}
    assert not cbm.should_compress(packet_ok, budget)
    
    packet_heavy = {"items": [{"estimated_tokens": 3500}]}
    assert cbm.should_compress(packet_heavy, budget)

def test_context_budget_manager_enforce_budget_preserves_critical_and_kinds():
    cbm = ContextBudgetManager()
    budget = {"total_budget": 100}
    
    context = {
        "items": [
            {"id": "crit", "priority": "critical", "estimated_tokens": 40},
            {"id": "mission_item", "kind": "mission", "priority": "medium", "estimated_tokens": 40},
            {"id": "low", "priority": "low", "estimated_tokens": 50},
        ]
    }
    
    res = cbm.enforce_budget(context, budget)
    ids = [item["id"] for item in res["items"]]
    assert "crit" in ids
    assert "mission_item" in ids # Preserved by kind
    assert "low" not in ids

def test_context_budget_manager_enforce_budget_drops_vs_compress():
    cbm = ContextBudgetManager()
    budget = {"total_budget": 100}
    
    context = {
        "items": [
            {"id": "crit", "priority": "critical", "estimated_tokens": 80},
            {"id": "med_ref", "priority": "medium", "ref": "doc1", "estimated_tokens": 50},
            {"id": "low_no_ref", "priority": "low", "estimated_tokens": 50},
        ]
    }
    
    res = cbm.enforce_budget(context, budget)
    assert "med_ref" in res["compressed_refs"]
    assert "low_no_ref" in res["dropped_refs"]

def test_context_budget_manager_enforce_budget_drops_by_priority():
    cbm = ContextBudgetManager()
    budget = {"total_budget": 150}
    
    context = {
        "items": [
            {"id": "i1", "priority": "high", "estimated_tokens": 70},
            {"id": "i2", "priority": "medium", "estimated_tokens": 70},
            {"id": "i3", "priority": "low", "estimated_tokens": 70},
        ]
    }
    
    # Budget is 150. i1+i2 = 140. i3 must be dropped.
    res = cbm.enforce_budget(context, budget)
    assert len(res["items"]) == 2
    ids = [item["id"] for item in res["items"]]
    assert "i1" in ids
    assert "i2" in ids
    assert "i3" not in ids
    assert "i3" in res["dropped_refs"]

def test_context_budget_manager_summarize_pressure():
    cbm = ContextBudgetManager()
    budget = {"total_budget": 1000}
    
    packet = {"items": [{"estimated_tokens": 950}]}
    summary = cbm.summarize_budget_pressure(packet, budget)
    assert summary["pressure"] == "high"
    assert summary["ratio"] == 0.95
