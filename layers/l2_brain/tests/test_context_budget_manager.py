import unittest
from layers.l2_brain.context_budget_manager import ContextBudgetManager

class TestContextBudgetManager(unittest.TestCase):
    def setUp(self):
        self.manager = ContextBudgetManager(default_max_tokens=10000)

    def test_allocate_and_usage(self):
        budget = self.manager.allocate_budget("sess1", "miss1", max_tokens=5000)
        self.assertEqual(budget["max_tokens"], 5000)
        
        self.manager.update_usage("miss1", 1000)
        self.assertEqual(self.manager.budgets["miss1"]["consumed_tokens"], 1000)

    def test_should_compress(self):
        self.manager.allocate_budget("sess2", "miss2", max_tokens=1000)
        # 700 + 150 = 850 (85%) > 80%
        self.manager.update_usage("miss2", 700)
        self.assertTrue(self.manager.should_compress("miss2", 150))
        
        # 500 + 100 = 600 (60%) < 80%
        self.manager.allocate_budget("sess3", "miss3", max_tokens=1000)
        self.manager.update_usage("miss3", 500)
        self.assertFalse(self.manager.should_compress("miss3", 100))

    def test_summarize_pressure(self):
        self.manager.allocate_budget("sess4", "miss4", max_tokens=1000)
        self.manager.update_usage("miss4", 950)
        pressure = self.manager.summarize_budget_pressure("sess4")
        self.assertEqual(pressure["status"], "critical")
        self.assertEqual(pressure["avg_pressure"], 0.95)

if __name__ == "__main__":
    unittest.main()
