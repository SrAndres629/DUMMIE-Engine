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

    def test_outcome_evaluator_calculates_positive_cas(self):
        result = OutcomeEvaluator().calculate_capability_amplification(
            current_metrics={
                "tests_passed": True,
                "input_tokens": 700,
                "cached_tokens": 100,
                "output_tokens": 300,
                "latency_ms": 700,
                "human_interventions": 1,
                "regressions": 0,
                "memory_reuse_gain": 0.5,
                "mentor_quality_gain": 0.25,
            },
            baseline_metrics={
                "tests_passed": False,
                "input_tokens": 1000,
                "cached_tokens": 0,
                "output_tokens": 500,
                "latency_ms": 1000,
                "human_interventions": 3,
                "regressions": 2,
                "memory_reuse_gain": 0.0,
                "mentor_quality_gain": 0.0,
            },
        )

        self.assertGreater(result.score, 0)
        self.assertEqual(result.verdict, "improved")
        self.assertEqual(result.next, "continue_collecting_metrics")

    def test_outcome_evaluator_calculates_negative_cas(self):
        result = OutcomeEvaluator().calculate_capability_amplification(
            current_metrics={
                "tests_passed": False,
                "input_tokens": 1600,
                "output_tokens": 900,
                "latency_ms": 1600,
                "human_interventions": 5,
                "regressions": 3,
                "memory_reuse_gain": -0.25,
                "mentor_quality_gain": -0.25,
            },
            baseline_metrics={
                "tests_passed": True,
                "input_tokens": 900,
                "output_tokens": 500,
                "latency_ms": 800,
                "human_interventions": 1,
                "regressions": 0,
                "memory_reuse_gain": 0.25,
                "mentor_quality_gain": 0.25,
            },
        )

        self.assertLess(result.score, 0)
        self.assertEqual(result.verdict, "regressed")
        self.assertEqual(result.next, "inspect_regression_causes")

    def test_outcome_evaluator_requires_baseline_for_cas(self):
        result = OutcomeEvaluator().calculate_capability_amplification(
            current_metrics={"tests_passed": True},
            baseline_metrics=None,
        )

        self.assertEqual(result.score, 0)
        self.assertEqual(result.verdict, "insufficient_baseline")
        self.assertEqual(result.next, "collect_more_metrics")

    def test_build_outcome_without_daemon(self):
        evaluator_no_daemon = OutcomeEvaluator()
        saga = SagaTransaction(
            transaction_id="tx789",
            context_token="tok_ghi",
            steps=[]
        )
        outcome = evaluator_no_daemon.build_outcome(
            status="SUCCESS",
            transaction_id="tx789",
            saga=saga
        )
        self.assertEqual(outcome["metacognition_status"], "UNKNOWN")
        self.assertEqual(outcome["gateway_first_policy"], "UNKNOWN")
        self.assertNotIn("efficiency", outcome)

if __name__ == "__main__":
    unittest.main()
