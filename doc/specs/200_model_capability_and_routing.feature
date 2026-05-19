Feature: Model Capability and Routing
  As a Cognitive Orchestrator
  I want to route tasks to the best available models
  So that I can optimize for cost, latency, and expertise

  Scenario: Route a coding task to a coding specialist
    Given a registry with a "coding-specialist" model and a "general-reasoner" model
    When I route an "EXECUTE_COMMAND" intent
    Then the "coding-specialist" model should be selected

  Scenario: Route a general task to a reasoner
    Given a registry with a "coding-specialist" model and a "general-reasoner" model
    When I route a "RESOLUTION" intent
    Then the "general-reasoner" model should be selected

  Scenario: Fallback to default when no specialist found
    Given a registry with only a "default-model"
    When I route a "VISION" intent
    Then the "default-model" should be selected
