Feature: Cognitive Crystallization Protocol
  As a Sovereign Agent
  I want to register my learnings and decisions in real-time
  In order to prevent technical debt and recurring errors

  Background:
    Given I have identified a critical architectural decision or lesson
    And the .aiwg/memory/ directory is writable

  Scenario: Crystallize a Lesson Learned
    When I encounter a syntax error or a logical failure
    And I resolve it after self-reflection
    Then I must append a new entry to .aiwg/memory/lessons.jsonl
    And the entry must be valid JSONL
    And Performance Metric: crystallization_latency < 500ms

  Scenario: Crystallize an Ambiguity Resolution
    When the PAH (Human) provides an answer to a technical indeterminacy
    Then I must append the resolution to .aiwg/memory/ambiguities.jsonl
    And I must update the local context with the new truth
    And Performance Metric: consistency_score == 1.0
