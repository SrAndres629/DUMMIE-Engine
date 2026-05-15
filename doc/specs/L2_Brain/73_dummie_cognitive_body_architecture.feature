Feature: DUMMIE Cognitive Body Architecture
  Scenario: Cognitive input classification
    Given a user message with operational intent
    When the message passes through the CognitiveHookPipeline
    Then it must be correctly classified by authority level
    And Performance Metric: latency < 100ms
    And include reasoning mode hints