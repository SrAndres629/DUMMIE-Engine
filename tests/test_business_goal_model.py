from layers.l2_brain.business_goal_model import GoalClassification, BusinessIntake, ToolOpportunity, GoalMemoryEntry

def test_models_serialization():
    gc = GoalClassification("revenue", 0.95, "desc")
    assert gc.to_dict()["goal_type"] == "revenue"

    bi = BusinessIntake("my goal", 10000.0)
    assert bi.to_dict()["target_mrr"] == 10000.0

    to = ToolOpportunity("calculator", "calc tool", "calculator")
    assert to.to_dict()["name"] == "calculator"
