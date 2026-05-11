import unittest
from unittest.mock import MagicMock
from layers.l2_brain.outcome_evaluator import OutcomeEvaluator
from layers.l2_brain.gateway_contract import SagaTransaction, SagaStep

class TestOutcomeEvaluator(unittest.TestCase):
    def setUp(self):
        self.mock_daemon = MagicMock()
        self.mock_daemon.metacognition_status = "READY"
        self.mock_daemon.gateway_policy.mode.value = "WARN"
        self.mock_daemon.last_cognitive_preflight = {"status": "SUCCESS"}
        self.evaluator = OutcomeEvaluator(self.mock_daemon)

    def test_build_outcome_basic(self):
        saga = SagaTransaction(
            transaction_id="tx123",
            context_token="tok_abc",
            steps=[SagaStep(task_id="step1", status="SUCCESS")]
        )
        outcome = self.evaluator.build_outcome(
            status="SUCCESS",
            transaction_id="tx123",
            saga=saga
        )

        self.assertEqual(outcome["status"], "SUCCESS")
        self.assertEqual(outcome["transaction_id"], "tx123")
        self.assertEqual(outcome["metacognition_status"], "READY")
        self.assertEqual(outcome["gateway_first_policy"], "WARN_MODE_ACTIVE")
        self.assertEqual(len(outcome["steps"]), 1)

    def test_build_outcome_with_efficiency(self):
        # Mock runtime meter
        self.mock_daemon.runtime_meter.get_stats.return_value = {
            "token_reduction_ratio": 0.75,
            "confidence": "high"
        }

        saga = SagaTransaction(transaction_id="tx456", context_token="tok_def", steps=[])
        outcome = self.evaluator.build_outcome(
            status="SUCCESS",
            transaction_id="tx456",
            saga=saga
        )

        self.assertIn("efficiency", outcome)
        self.assertEqual(outcome["efficiency"]["token_reduction_ratio"], 0.75)

    def test_enrich_with_metacognition(self):
        frame = MagicMock()
        frame.authority_level = "A1"
        frame.mission_plan = [1, 2, 3]
        frame.verification_findings = ["find1"]
        frame.required_tools = ["tool1"]
        frame.risk_level = "low"

        outcome = {"base": "data"}
        enriched = self.evaluator.enrich_with_metacognition(outcome, frame)

        self.assertIn("metacognition", enriched)
        self.assertEqual(enriched["metacognition"]["authority"], "A1")
        self.assertEqual(enriched["metacognition"]["mission_steps"], 3)

if __name__ == "__main__":
    unittest.main()
