from layers.l2_brain.strategic_partner_runtime import StrategicPartnerRuntime

def test_advisor_revenue_flow():
    runtime = StrategicPartnerRuntime()
    res = runtime.advise("quiero ganar 10000 USD al mes")
    assert res["goal_classification"]["goal_type"] == "revenue"
    assert res["business_intake"]["target_mrr"] == 10000.0
    assert len(res["strategic_questions"]) > 0
    assert len(res["tool_opportunities"]) > 0
