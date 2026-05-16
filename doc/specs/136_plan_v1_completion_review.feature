Feature: Plan V1 Completion Review
  As an Evaluator
  I want to score implemented capabilities
  So that the progress of Plan V1 is empirically verified.

  Scenario: Score implemented feature
    When PlanV1CompletionReview runs
    Then the Context Compressor should score > 0
    And its status should not be 'missing'.
