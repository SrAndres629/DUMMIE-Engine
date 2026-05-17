Feature: Runtime Closure Planner
  As a Metacognitive Configuration Architect,
  I want to translate degraded capabilities into actionable closure plans,
  So that operators have safe, step-by-step commands to repair physical dependencies.

  Scenario: Plan generation for degraded capabilities
    Given a consolidated degraded capability registry
    When the runtime closure planner compiles a closure plan
    Then it should create repair sequences for kuzu_4dtes_persistence
    And it should set all install_dependency actions to can_execute_now: false
    And it should set requires_human_approval to true
    And it should provide verification and rollback steps
    And it should write the latest closure plan reports
