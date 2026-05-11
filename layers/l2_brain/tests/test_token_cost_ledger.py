import unittest
from layers.l2_brain.token_cost_ledger import TokenCostLedger

class TestTokenCostLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = TokenCostLedger()

    def test_record_usage_and_summary(self):
        self.ledger.record_usage({
            "session_id": "sess1",
            "mission_id": "miss1",
            "model_tier": "cloud_std",
            "input_tokens": 1000,
            "output_tokens": 200
        })
        
        self.ledger.record_usage({
            "session_id": "sess1",
            "mission_id": "miss1",
            "model_tier": "local_fast",
            "input_tokens": 500,
            "output_tokens": 50
        })
        
        summary = self.ledger.summarize_mission("miss1")
        self.assertEqual(summary["total_input"], 1500)
        self.assertEqual(summary["total_output"], 250)
        self.assertEqual(summary["event_count"], 2)
        self.assertIn("cloud_std", summary["tiers"])
        self.assertIn("local_fast", summary["tiers"])

    def test_cache_hit_ratio(self):
        self.ledger.record_usage({
            "session_id": "sess2",
            "input_tokens": 800,
            "cached_tokens": 200,
            "output_tokens": 100
        })
        ratio = self.ledger.cache_hit_ratio("sess2")
        self.assertEqual(ratio, 0.2)

    def test_cloud_cost_estimate(self):
        self.ledger.record_usage({
            "session_id": "sess3",
            "model_tier": "cloud_prem",
            "input_tokens": 1000000, # 1M tokens
            "output_tokens": 1000000
        })
        estimate = self.ledger.cloud_cost_estimate("sess3")
        # 1M input (15.0) + 1M output (60.0) = 75.0
        self.assertEqual(estimate["estimated_total"], 75.0)

if __name__ == "__main__":
    unittest.main()
